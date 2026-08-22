"""Service to generate all UML diagrams for a project (with raw_input context passed to all generators)"""
from typing import Dict, List, Optional
from backend.app.modules.module_10_uml_generator import (
    UseCaseGenerator, ClassDiagramGenerator, SequenceGenerator, ActivityGenerator,
    PlantUMLRenderer,
    ObjectDiagramGenerator, StateDiagramGenerator, ComponentDiagramGenerator
)
from backend.app.database.models import Project, Requirement, Diagram
from sqlalchemy.orm import Session


class UMLService:
    @classmethod
    def generate_diagrams(cls, project_id: int, db: Session) -> Dict:
        """Generate all 7 diagram types for a project using project description context."""
        requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        if not requirements:
            return {"message": "No requirements found", "project_id": project_id}

        # Delete all existing diagrams for this project to avoid duplicates
        db.query(Diagram).filter(Diagram.project_id == project_id).delete()

        req_list = [{"id": r.id, "text": r.text, "requirement_id": r.requirement_id} for r in requirements]
        project = db.query(Project).filter(Project.id == project_id).first()
        domain = project.domain if project else "general"
        raw_input = project.raw_input if project else ""

        results = {}

        # 1. Use Case diagram
        uc_result = UseCaseGenerator.generate(req_list, raw_input=raw_input, domain=domain)
        results["use_case"] = uc_result
        db.add(Diagram(
            diagram_type="use_case",
            title=f"Use Case Diagram – {project.project_id}",
            plantuml_code=uc_result["plantuml"],
            project_id=project_id
        ))

        # 2. Class diagram
        class_result = ClassDiagramGenerator.generate(req_list, raw_input=raw_input, domain=domain)
        results["class_diagram"] = class_result
        db.add(Diagram(
            diagram_type="class_diagram",
            title=f"Class Diagram – {project.project_id}",
            plantuml_code=class_result["plantuml"],
            project_id=project_id
        ))

        # 3. Sequence diagram
        seq_result = SequenceGenerator.generate(req_list, raw_input=raw_input, domain=domain)
        results["sequence_diagram"] = seq_result
        db.add(Diagram(
            diagram_type="sequence_diagram",
            title=f"Sequence Diagram – {project.project_id}",
            plantuml_code=seq_result["plantuml"],
            project_id=project_id
        ))

        # 4. Activity diagram
        act_result = ActivityGenerator.generate(req_list, raw_input=raw_input, domain=domain)
        results["activity_diagram"] = act_result
        db.add(Diagram(
            diagram_type="activity_diagram",
            title=f"Activity Diagram – {project.project_id}",
            plantuml_code=act_result["plantuml"],
            project_id=project_id
        ))

        # 5. Object diagram
        obj_result = ObjectDiagramGenerator.generate(
            classes=class_result.get("classes", []),
            attributes=class_result.get("attributes", {}),
            raw_input=raw_input,
            domain=domain
        )
        results["object_diagram"] = obj_result
        db.add(Diagram(
            diagram_type="object_diagram",
            title=f"Object Diagram – {project.project_id}",
            plantuml_code=obj_result["plantuml"],
            project_id=project_id
        ))

        # 6. State diagram
        state_result = StateDiagramGenerator.generate(req_list, raw_input=raw_input, domain=domain)
        results["state_diagram"] = state_result
        db.add(Diagram(
            diagram_type="state_diagram",
            title=f"State Diagram – {project.project_id}",
            plantuml_code=state_result["plantuml"],
            project_id=project_id
        ))

        # 7. Component diagram
        comp_result = ComponentDiagramGenerator.generate(requirements=req_list, raw_input=raw_input, domain=domain)
        results["component_diagram"] = comp_result
        db.add(Diagram(
            diagram_type="component_diagram",
            title=f"Component Diagram – {project.project_id}",
            plantuml_code=comp_result["plantuml"],
            project_id=project_id
        ))

        db.commit()

        all_diagrams = db.query(Diagram).filter(Diagram.project_id == project_id).all()
        return {
            "project_id": project.project_id,
            "diagrams_generated": 7,
            "diagram_ids": [d.id for d in all_diagrams],
            "details": results
        }

    @classmethod
    def render_diagram(cls, diagram_id: int, db: Session, format: str = "png") -> Dict:
        """Render a specific diagram to image format (returns base64 for PNG or raw SVG)"""
        diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
        if not diagram:
            return {"error": "Diagram not found"}

        if format == "png":
            png_bytes = PlantUMLRenderer.render_to_png(diagram.plantuml_code)
            if png_bytes:
                import base64
                return {"png_base64": base64.b64encode(png_bytes).decode('utf-8')}
        elif format == "svg":
            svg_text = PlantUMLRenderer.render_to_svg(diagram.plantuml_code)
            if svg_text:
                return {"svg": svg_text}

        return {"error": "Rendering failed"}

    @classmethod
    def get_diagram_plantuml(cls, diagram_id: int, db: Session) -> Dict:
        """Get raw PlantUML code for a diagram"""
        diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
        if not diagram:
            return {"error": "Diagram not found"}
        return {"plantuml_code": diagram.plantuml_code, "type": diagram.diagram_type}

    @classmethod
    def update_diagram_code(cls, diagram_id: int, new_code: str, db: Session) -> Dict:
        """Update the PlantUML code for a diagram and return success."""
        diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
        if not diagram:
            return {"error": "Diagram not found"}
        
        diagram.plantuml_code = new_code
        db.commit()
        return {"message": "Diagram updated", "id": diagram_id}

    @staticmethod
    def render_diagram_image(diagram_id: int, db: Session, format: str = "png") -> Optional[bytes]:
        """Return raw image bytes for a diagram (PNG or SVG as bytes). Used by ZIP export."""
        diagram = db.query(Diagram).filter(Diagram.id == diagram_id).first()
        if not diagram:
            return None
        if format == "png":
            return PlantUMLRenderer.render_to_png(diagram.plantuml_code)
        elif format == "svg":
            svg_str = PlantUMLRenderer.render_to_svg(diagram.plantuml_code)
            return svg_str.encode() if svg_str else None
        return None