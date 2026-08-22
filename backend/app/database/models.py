"""Database models for DocuForge AI"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Enum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.connection import Base
import enum

# Enums for requirement types
class RequirementType(str, enum.Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    CONSTRAINT = "constraint"

class Priority(str, enum.Enum):
    MUST = "must"
    SHOULD = "should"
    COULD = "could"
    WONT = "wont"

class ConflictSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DocumentType(str, enum.Enum):
    SRS = "srs"
    SOW = "sow"
    TEST_PLAN = "test_plan"
    DEPLOYMENT_GUIDE = "deployment_guide"
    COMPLIANCE = "compliance"

class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    CLARIFYING = "clarifying"
    COMPLETE = "complete"
    EXPORTED = "exported"

# Table 1: Users
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    api_key = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Jira
    jira_base_url = Column(String(255))
    jira_email = Column(String(255))
    jira_api_token = Column(String(255))
    
    # GitHub
    github_token = Column(String(255))
    github_username = Column(String(255))
    
    # Slack
    slack_webhook_url = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="settings")

# Table 2: Projects
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), unique=True, index=True, nullable=False)  # User-friendly ID
    name = Column(String(255), nullable=False)
    description = Column(Text)
    domain = Column(String(100), index=True)
    subdomain = Column(String(100))
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    raw_input = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="project", cascade="all, delete-orphan")
    diagrams = relationship("Diagram", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    clarification_session = relationship("ClarificationSession", back_populates="project", uselist=False, cascade="all, delete-orphan")

# Table 3: Requirements
class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(String(50), index=True, nullable=False)  # FR-001 format
    text = Column(Text, nullable=False)
    type = Column(Enum(RequirementType), nullable=False)
    category = Column(String(100))
    priority = Column(Enum(Priority), default=Priority.SHOULD)
    priority_confidence = Column(Float, default=0.0)
    complexity = Column(Integer, default=1)  # 1-10
    effort_hours = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    business_value = Column(Integer, default=0)  # 0-100
    source = Column(String(100))  # user_input, inferred, pattern
    testability = Column(String(50))
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    parent_id = Column(Integer, ForeignKey("requirements.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="requirements")
    parent = relationship("Requirement", remote_side=[id], foreign_keys=[parent_id])
    
    # Indexes
    __table_args__ = (
        Index('ix_requirements_project_type', 'project_id', 'type'),
        Index('ix_requirements_project_priority', 'project_id', 'priority'),
    )

# Table 4: Conflicts
class Conflict(Base):
    __tablename__ = "conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    conflict_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(ConflictSeverity), default=ConflictSeverity.MEDIUM)
    resolution = Column(Text)
    resolved = Column(Boolean, default=False)
    resolution_accepted = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    requirement_id_1 = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    requirement_id_2 = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="conflicts")
    req1 = relationship("Requirement", foreign_keys=[requirement_id_1])
    req2 = relationship("Requirement", foreign_keys=[requirement_id_2])

# Table 5: Clarification Sessions
class ClarificationSession(Base):
    __tablename__ = "clarification_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_data = Column(JSON, default=dict)  # Stores all Q&A
    assumptions = Column(JSON, default=list)  # Stores logged assumptions
    current_question_index = Column(Integer, default=0)
    is_complete = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    project = relationship("Project", back_populates="clarification_session")

# Table 6: Diagrams
class Diagram(Base):
    __tablename__ = "diagrams"
    
    id = Column(Integer, primary_key=True, index=True)
    diagram_type = Column(String(50), nullable=False)  # use_case, class, sequence, activity
    title = Column(String(255))
    plantuml_code = Column(Text, nullable=False)
    png_data = Column(Text, nullable=True)  # Base64 encoded or S3 path
    svg_data = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    project = relationship("Project", back_populates="diagrams")

# Table 7: Documents
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    format = Column(String(20), nullable=False)  # pdf, docx, html, json
    file_path = Column(String(500), nullable=False)
    page_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)  # in bytes
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    project = relationship("Project", back_populates="documents")

# Table 8: Learning Data (for AI improvement)
class LearningData(Base):
    __tablename__ = "learning_data"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(500))
    user_action = Column(Text)
    success_rate = Column(Float, default=0.0)
    frequency = Column(Integer, default=1)
    domain = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
