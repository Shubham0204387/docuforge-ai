"""DocuForge AI - Main Application Entry Point"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db, engine
from backend.app.database.models import Base, User, Project, Requirement, Conflict, Diagram, UserSettings
from backend.app.api.routes import auth
from backend.app.api.schemas.settings import UserSettingsSchema
from backend.app.services.uml_service import UMLService
from backend.app.modules.module_1_input_processor import FormatDetector, InputValidator, DomainClassifier, BulkProcessor

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="DocuForge AI",
    description="AI-Powered Requirements Engineering Platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "DocuForge AI API is running!",
        "status": "healthy",
        "version": "0.1.0",
        "modules": ["Module 1: Input Processor Active"]
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
from backend.app.api.schemas.project import ProjectInput

@app.post("/api/process-input")
async def process_input(
    input_data: ProjectInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    text = input_data.text
    """
    Process user input through Module 1, then auto-runs full pipeline:
    Extract → Formalize → Expand (inference) → Prioritize → Quality Assessment → Conflict Detection
    Returns: project_id and summary counts
    """
    from backend.app.services.inference_service import InferenceService
    from backend.app.services.formalization_service import FormalizationService
    from backend.app.services.conflict_service import ConflictDetectionService
    from backend.app.services.prioritization_service import PrioritizationService
    from backend.app.services.quality_service import QualityAssessmentService

    # Step 1: Detect format
    format_info = FormatDetector.detect(text)

    # Step 2: Validate input
    validation = InputValidator.validate(text)

    # Step 3: Classify domain
    domain = DomainClassifier.classify(text)

    # Step 4: Extract requirements
    requirements = BulkProcessor.extract_requirements(text)

    # Step 5: Create project (sequential PROJ_XXXX)
    last_project = db.query(Project).order_by(Project.id.desc()).first()
    next_num = (last_project.id + 1) if last_project else 1
    project_id_str = f"PROJ_{next_num:04d}"
    
    project = Project(
        project_id=project_id_str,
        name=text[:60].strip() if text else f"Project_{next_num}",
        raw_input=text,
        domain=domain["domain"],
        user_id=current_user.id,
        status="processing"
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Step 6: Store extracted requirements
    for req in requirements:
        requirement = Requirement(
            requirement_id=f"RAW_{req['line_number']:03d}",
            text=req["text"],
            type="functional",
            project_id=project.id,
            source="user_input"
        )
        db.add(requirement)
    db.commit()

    # Step 7: Auto-pipeline (best-effort – errors are non-fatal)
    try:
        # 7a: Formalize requirements (IEEE 830 format)
        FormalizationService().formalize_project_requirements(project.id, db) if hasattr(FormalizationService(), 'formalize_project_requirements') else None
    except Exception as e:
        print(f"Formalization warning: {e}")
    try:
        # 7b: Expand with knowledge graph inference
        InferenceService().expand_project_requirements(project.id, db)
    except Exception as e:
        print(f"Expansion warning: {e}")
    try:
        # 7c: Prioritize (MoSCoW)
        PrioritizationService.prioritize_project(project.id, db)
    except Exception as e:
        print(f"Prioritization warning: {e}")
    try:
        # 7d: Quality assessment
        QualityAssessmentService.assess_project(project.id, db)
    except Exception as e:
        print(f"Quality warning: {e}")
    try:
        # 7e: Conflict detection
        ConflictDetectionService.detect_all_conflicts(project.id, db)
    except Exception as e:
        print(f"Conflict detection warning: {e}")

    # Re-fetch to count final requirements
    final_req_count = db.query(Requirement).filter(Requirement.project_id == project.id).count()

    # Update project status
    project.status = "complete"
    db.commit()

    return {
        "project_id": project.project_id,
        "format": format_info,
        "validation": validation,
        "domain": domain,
        "extracted_requirements": requirements,
        "requirements_count": final_req_count,
        "status": "complete"
    }


@app.get("/api/projects")
async def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Get all projects for current user"""
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return [
        {
            "id": p.project_id,
            "name": p.name,
            "domain": p.domain,
            "status": p.status.value,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "requirements_count": len(p.requirements)
        }
        for p in projects
    ]


@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Delete a project and all its data"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully", "project_id": project_id}


@app.get("/api/projects/{project_id}/requirements")
async def get_project_requirements(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Get all requirements for a project (with priority, RQI, category, source)"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    def _priority_label(r):
        try:
            return r.priority.value if r.priority else "SHOULD"
        except Exception:
            return "SHOULD"

    return [
        {
            "id": r.requirement_id,
            "requirement_id": r.requirement_id,
            "text": r.text,
            "type": r.type.value if r.type else "functional",
            "priority": _priority_label(r),
            "rqi_score": round(r.quality_score or r.priority_confidence * 100 if r.priority_confidence else 0, 1),
            "quality_score": round(r.quality_score or 0, 1),
            "category": r.category or "General",
            "source": r.source or "user_input",
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in project.requirements
    ]


# Import clarification routes
from backend.app.api.routes import clarification
app.include_router(clarification.router, prefix="/api")


from backend.app.services.nlp_service import NLPService


@app.post("/api/analyze-requirement")
async def analyze_requirement(
    text: str,
    domain: str = "general",
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Analyze a single requirement using NLP (Module 3)"""
    analysis = NLPService.analyze_requirement(text, domain)
    return analysis


@app.post("/api/analyze-project/{project_id}")
async def analyze_project_requirements(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Analyze all requirements of a project using NLP"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    requirements = project.requirements
    req_list = [{"id": r.requirement_id, "text": r.text} for r in requirements]
    analyses = NLPService.batch_analyze(req_list, project.domain)
    
    # Optionally update requirement types based on intent classification
    for analysis in analyses:
        req_id = analysis["requirement_id"]
        intent_type = analysis["analysis"]["intent"]["type"]
        req = db.query(Requirement).filter(Requirement.requirement_id == req_id, Requirement.project_id == project.id).first()
        if req:
            req.type = intent_type
    db.commit()
    
    return {
        "project_id": project_id,
        "requirements_analyzed": len(analyses),
        "analyses": analyses
    }


from backend.app.services.inference_service import InferenceService


@app.post("/api/expand-project/{project_id}")
async def expand_project_requirements(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Expand project requirements using knowledge graph (Module 4)"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    inference_service = InferenceService()
    result = inference_service.expand_project_requirements(project.id, db)
    return result


@app.post("/api/expand-text")
async def expand_text(
    text: str,
    domain: str = "general",
    current_user: User = Depends(auth.get_current_user)
):
    """Expand a single text using inference rules"""
    inference_service = InferenceService()
    result = inference_service.expand_single_text(text, domain)
    return result


from backend.app.services.formalization_service import FormalizationService


@app.post("/api/formalize-requirement")
async def formalize_requirement(
    text: str,
    req_type: str = "functional",
    current_user: User = Depends(auth.get_current_user)
):
    """Convert a single requirement to formal IEEE 830 format"""
    service = FormalizationService()
    result = service.formalize_requirement(text, req_type)
    return result


@app.post("/api/formalize-project/{project_id}")
async def formalize_project_requirements(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Convert all requirements in a project to formal format"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    service = FormalizationService()
    result = service.formalize_project_requirements(project.id, db)
    return result


@app.post("/api/generate-formal-from-expansion/{project_id}")
async def generate_formal_from_expansion(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Generate formal requirements from previously expanded inferences"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    from backend.app.services.inference_service import InferenceService
    inference_service = InferenceService()
    inference_service.expand_project_requirements(project.id, db)  # just to ensure expansion exists
    
    service = FormalizationService()
    result = service.formalize_project_requirements(project.id, db)
    
    return {
        "message": "Formalization complete",
        "project_id": project_id,
        "requirements_processed": result.get("requirements_processed", 0),
        "formalized_count": result.get("formalized_count", 0)
    }


from backend.app.services.conflict_service import ConflictDetectionService


@app.post("/api/conflicts/detect/{project_id}")
async def detect_conflicts(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Detect conflicts for all requirements in a project"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = ConflictDetectionService.detect_all_conflicts(project.id, db)
    return result


@app.post("/api/conflicts/resolve/{conflict_id}")
async def resolve_conflict(
    conflict_id: int,
    resolution: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Resolve a conflict by providing a resolution text"""
    conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")
    project = db.query(Project).filter(Project.id == conflict.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = ConflictDetectionService.resolve_conflict(conflict_id, resolution, db)
    return result


@app.get("/api/conflicts/{project_id}")
async def get_conflicts(
    project_id: str,
    unresolved_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Get all conflicts for a project"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    query = db.query(Conflict).filter(Conflict.project_id == project.id)
    if unresolved_only:
        query = query.filter(Conflict.resolved == False)
    
    conflicts = query.all()
    return [
        {
            "id": c.id,
            "type": c.conflict_type,
            "description": c.description,
            "severity": c.severity.value,
            "resolved": c.resolved,
            "resolution": c.resolution
        } for c in conflicts
    ]


from backend.app.services.impact_service import ImpactAnalysisService


@app.post("/api/impact/{project_id}")
async def analyze_impact(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Run full impact analysis on a project (Complexity, Effort, Dependencies, Risk)"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = ImpactAnalysisService.analyze_project(project.id, db)
    return result


@app.get("/api/impact/{project_id}/dependencies")
async def get_dependency_graph(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Get the dependency graph for a project"""
    from backend.app.modules.module_7_impact_analyzer import DependencyMapper
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
    req_list = [{"requirement_id": r.requirement_id, "text": r.text} for r in requirements]
    graph = DependencyMapper.build_dependency_graph(req_list)
    return graph


# ========== PHASE 8: QUALITY ASSESSMENT ENGINE ==========
from backend.app.services.quality_service import QualityAssessmentService


@app.post("/api/quality/requirement")
async def assess_single_requirement(
    text: str,
    current_user: User = Depends(auth.get_current_user)
):
    """Run quality assessment on a single requirement text (for testing)"""
    result = QualityAssessmentService.assess_requirement(text)
    return result


@app.post("/api/quality/{project_id}")
async def assess_project_quality(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Run quality assessment on all requirements in a project"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = QualityAssessmentService.assess_project(project.id, db)
    return result
# ========== END PHASE 8 ==========


# ========== PHASE 9: PRIORITIZATION & COMPLIANCE ==========
from backend.app.services.prioritization_service import PrioritizationService

@app.post("/api/prioritize/requirement")
async def prioritize_single_requirement(
    text: str,
    domain: str = "general",
    complexity: int = 5,
    category: str = None,
    current_user: User = Depends(auth.get_current_user)
):
    """Prioritize a single requirement (for testing)"""
    result = PrioritizationService.prioritize_single_requirement(text, domain, complexity, category)
    return result

@app.post("/api/prioritize/{project_id}")
async def prioritize_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Run full prioritization (MoSCoW, business value, compliance, adjustments) on a project"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = PrioritizationService.prioritize_project(project.id, db)
    return result

@app.get("/api/compliance/regulations")
async def list_regulations(current_user: User = Depends(auth.get_current_user)):
    """List all supported compliance regulations"""
    from backend.app.modules.module_9_prioritizer.compliance_mapper import ComplianceMapper
    regulations = list(ComplianceMapper.REGULATIONS.keys())
    return {"regulations": regulations}
# ========== END PHASE 9 ==========

# ========== PHASE 10: UML DIAGRAM GENERATOR ==========
from backend.app.services.uml_service import UMLService

@app.post("/api/uml/generate/{project_id}")
async def generate_uml_diagrams(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Generate all UML diagrams for a project and store in database"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = UMLService.generate_diagrams(project.id, db)
    return result

@app.get("/api/uml/diagram/{diagram_id}")
async def get_diagram_plantuml(
    diagram_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Get the PlantUML code for a specific diagram"""
    diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    # Verify user has access to project
    project = db.query(Project).filter(Project.id == diagram.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    result = UMLService.get_diagram_plantuml(diagram_id, db)
    return result

@app.get("/api/uml/render/{diagram_id}")
async def render_diagram(
    diagram_id: int,
    format: str = "png",
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Render a diagram to PNG or SVG (returns base64 for PNG, raw SVG for SVG)"""
    diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    project = db.query(Project).filter(Project.id == diagram.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    result = UMLService.render_diagram(diagram_id, db, format)
    return result

# Download diagram as image file (PNG, JPG, TIFF, or SVG)
@app.get("/api/uml/download/{diagram_id}")
async def download_diagram_image(
    diagram_id: int,
    format: str = "png",
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Download a UML diagram as image file (PNG, JPG/JPEG, TIFF, or SVG)"""
    from backend.app.modules.module_10_uml_generator.plantuml_renderer import PlantUMLRenderer

    diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    project = db.query(Project).filter(Project.id == diagram.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")

    fmt = format.lower()

    if fmt == "svg":
        svg_text = PlantUMLRenderer.render_to_svg(diagram.plantuml_code)
        if not svg_text:
            raise HTTPException(status_code=500, detail="SVG rendering failed")
        return Response(content=svg_text, media_type="image/svg+xml",
                        headers={"Content-Disposition": f"attachment; filename={diagram.diagram_type}_{diagram.id}.svg"})

    # For PNG, JPG, JPEG, TIFF – render to PNG first then convert if needed
    png_bytes = PlantUMLRenderer.render_to_png(diagram.plantuml_code)
    if not png_bytes:
        raise HTTPException(status_code=500, detail="Rendering failed – ensure PlantUML is installed")

    if fmt == "png":
        return Response(content=png_bytes, media_type="image/png",
                        headers={"Content-Disposition": f"attachment; filename={diagram.diagram_type}_{diagram.id}.png"})

    # Convert PNG to JPG or TIFF using Pillow
    try:
        from PIL import Image
        import io as _io
        img = Image.open(_io.BytesIO(png_bytes)).convert("RGB")
        buf = _io.BytesIO()
        if fmt in ("jpg", "jpeg"):
            img.save(buf, format="JPEG", quality=95)
            media_type = "image/jpeg"
            ext = "jpg"
        elif fmt == "tiff":
            img.save(buf, format="TIFF")
            media_type = "image/tiff"
            ext = "tiff"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format '{format}'. Use: png, jpg, jpeg, tiff, svg")
        buf.seek(0)
        return Response(content=buf.read(), media_type=media_type,
                        headers={"Content-Disposition": f"attachment; filename={diagram.diagram_type}_{diagram.id}.{ext}"})
    except ImportError:
        raise HTTPException(status_code=500, detail="Pillow not installed; only PNG/SVG supported")


@app.get("/api/uml/project/{project_id}/diagrams")
async def get_project_diagrams(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """List all diagrams for a project"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    diagrams = db.query(Diagram).filter(Diagram.project_id == project.id).all()
    return [
        {
            "id": d.id,
            "type": d.diagram_type,
            "title": d.title,
            "plantuml_code": d.plantuml_code,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in diagrams
    ]
# ========== END PHASE 10 ==========

# ========== PHASE 11: DOCUMENTATION GENERATOR ==========
from backend.app.services.document_service import DocumentService
from fastapi.responses import Response, FileResponse
import tempfile
import base64

@app.post("/api/documents/generate/{project_id}")
async def generate_documents(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Generate all project documents (HTML) and return links or data"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    docs = DocumentService.generate_all_documents(project.id, db)
    # Return a summary
    return {
        "project_id": project_id,
        "documents_generated": {
            "srs": "html",
            "sow": "html",
            "test_plan": "html",
            "deployment_guide": "html",
            "compliance": "html"
        },
        "message": "Use download endpoints to get specific formats."
    }

@app.get("/api/documents/download/{project_id}/{doc_type}/{format}")
async def download_document(
    project_id: str,
    doc_type: str,
    format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Download a document (srs, sow, test_plan, deployment_guide, compliance) in pdf or docx"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    docs = DocumentService.generate_all_documents(project.id, db)
    if doc_type not in docs:
        raise HTTPException(status_code=404, detail="Document type not found")
    
    html_content = docs[doc_type]
    
    if format == "pdf":
        pdf_bytes = DocumentService.html_to_pdf(html_content)
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename={doc_type}_{project_id}.pdf"})
    elif format == "docx":
        docx_bytes = DocumentService.html_to_docx(html_content)
        return Response(content=docx_bytes, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        headers={"Content-Disposition": f"attachment; filename={doc_type}_{project_id}.docx"})
    else:
        # Return HTML as plain text
        return Response(content=html_content, media_type="text/html")
# ========== END PHASE 11 ==========

# ========== PHASE 12: OUTPUT & INTEGRATION ==========
from backend.app.services.integration_service import IntegrationService

@app.get("/api/export/zip/{project_id}")
async def export_zip(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Download entire project as ZIP archive (PDF documents + PNG diagrams)"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    zip_bytes = await IntegrationService.export_project_zip(project.id, db)
    return Response(content=zip_bytes, media_type="application/zip",
                    headers={"Content-Disposition": f"attachment; filename={project_id}_export.zip"})

@app.get("/api/dashboard/{project_id}")
async def get_dashboard(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Get interactive HTML dashboard for the project"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    html = await IntegrationService.generate_dashboard(project.id, db)
    return Response(content=html, media_type="text/html")

@app.post("/api/integrations/jira/{project_id}")
async def jira_integration(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Push requirements to Jira (requires JIRA_* environment variables)"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await IntegrationService.push_to_jira(project.id, db)
    return result

@app.post("/api/integrations/git/{project_id}")
async def git_integration(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Create GitHub repository and push documentation (requires GITHUB_TOKEN, GITHUB_OWNER)"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await IntegrationService.push_to_git(project.id, db)
    return result

@app.post("/api/integrations/slack/{project_id}")
async def slack_integration(
    project_id: str,
    message: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Send Slack notification (requires SLACK_WEBHOOK_URL)"""
    project = db.query(Project).filter(Project.project_id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await IntegrationService.send_slack_notification(project.id, db, message)
    return result

@app.get("/api/export/status")
async def export_status(current_user: User = Depends(auth.get_current_user)):
    """Check if external integrations are configured (for frontend)
    Returns which integrations are available."""
    import os
    return {
        "jira_configured": bool(os.getenv("JIRA_BASE_URL") and os.getenv("JIRA_EMAIL") and os.getenv("JIRA_API_TOKEN")),
        "git_configured": bool(os.getenv("GITHUB_TOKEN") and os.getenv("GITHUB_OWNER")),
        "slack_configured": bool(os.getenv("SLACK_WEBHOOK_URL"))
    }
# ========== END PHASE 12 ==========
# ========== SETTINGS & LIVE EDITOR ==========

@app.get("/api/settings", response_model=UserSettingsSchema)
async def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Get settings for the current user"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        # Create empty settings if not exists
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.put("/api/settings", response_model=UserSettingsSchema)
async def update_user_settings(
    settings_data: UserSettingsSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Update settings for the current user"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Update fields
    for field, value in settings_data.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    return settings

@app.put("/api/uml/diagrams/{diagram_id}")
async def update_diagram(
    diagram_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Update diagram PlantUML code (Live Editor)"""
    # Check if diagram belongs to user's project
    diagram = db.query(Diagram).join(Project).filter(Diagram.id == diagram_id, Project.user_id == current_user.id).first()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    new_code = data.get("plantuml_code")
    if not new_code:
        raise HTTPException(status_code=400, detail="plantuml_code is required")
        
    return UMLService.update_diagram_code(diagram_id, new_code, db)

@app.post("/api/chat/{project_id}")
async def project_chat(
    project_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    """Interactive AI Chat about project requirements"""
    from backend.app.services.chat_service import ChatService
    question = data.get("message")
    if not question:
        raise HTTPException(status_code=400, detail="Message is required")
    
    response = ChatService.ask_question(project_id, question, db)
    return {"response": response}
