"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Videos table
    op.create_table(
        'videos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('original_name', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=False),
        sa.Column('duration_secs', sa.Float, nullable=True),
        sa.Column('width', sa.Integer, nullable=True),
        sa.Column('height', sa.Integer, nullable=True),
        sa.Column('fps', sa.Float, nullable=True),
        sa.Column('codec', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='uploading'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Clips table
    op.create_table(
        'clips',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('video_id', UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('label', sa.String(200), nullable=True),
        sa.Column('start_time', sa.Float, nullable=False),
        sa.Column('end_time', sa.Float, nullable=False),
        sa.Column('duration_secs', sa.Float, nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('parent_clip_id', UUID(as_uuid=True), sa.ForeignKey('clips.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_clips_video_id', 'clips', ['video_id'])

    # Captions table
    op.create_table(
        'captions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('video_id', UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('model_size', sa.String(20), nullable=False),
        sa.Column('language', sa.String(10), nullable=True),
        sa.Column('full_text', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # Caption segments table
    op.create_table(
        'caption_segments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('caption_id', UUID(as_uuid=True), sa.ForeignKey('captions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('segment_index', sa.Integer, nullable=False),
        sa.Column('start_time', sa.Float, nullable=False),
        sa.Column('end_time', sa.Float, nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('words_json', JSONB, nullable=True),
    )
    op.create_index('idx_caption_segments_caption', 'caption_segments', ['caption_id', 'segment_index'])

    # Caption styles table
    op.create_table(
        'caption_styles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('caption_id', UUID(as_uuid=True), sa.ForeignKey('captions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('font_family', sa.String(100), nullable=False, server_default='Arial'),
        sa.Column('font_size', sa.Integer, nullable=False, server_default='48'),
        sa.Column('primary_color', sa.String(20), nullable=False, server_default='#FFFFFF'),
        sa.Column('outline_color', sa.String(20), nullable=False, server_default='#000000'),
        sa.Column('highlight_color', sa.String(20), nullable=False, server_default='#FFFF00'),
        sa.Column('highlight_words', ARRAY(sa.String), nullable=True),
        sa.Column('position', sa.String(20), nullable=False, server_default='bottom'),
        sa.Column('bold', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('animation_type', sa.String(30), nullable=False, server_default='none'),
    )

    # Jobs table
    op.create_table(
        'jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('celery_task_id', sa.String(200), unique=True, nullable=True),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('progress_pct', sa.Integer, nullable=False, server_default='0'),
        sa.Column('result_json', JSONB, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('retry_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('video_id', UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=True),
        sa.Column('clip_id', UUID(as_uuid=True), sa.ForeignKey('clips.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_jobs_status', 'jobs', ['status'])
    op.create_index('idx_jobs_video_id', 'jobs', ['video_id'])

    # Exports table
    op.create_table(
        'exports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('clip_id', UUID(as_uuid=True), sa.ForeignKey('clips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', UUID(as_uuid=True), sa.ForeignKey('jobs.id'), nullable=True),
        sa.Column('aspect_ratio', sa.String(10), nullable=False),
        sa.Column('platform', sa.String(30), nullable=True),
        sa.Column('width', sa.Integer, nullable=True),
        sa.Column('height', sa.Integer, nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=True),
        sa.Column('effects_json', JSONB, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_exports_clip_id', 'exports', ['clip_id'])

    # Highlights table
    op.create_table(
        'highlights',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('video_id', UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_time', sa.Float, nullable=False),
        sa.Column('end_time', sa.Float, nullable=False),
        sa.Column('score', sa.Float, nullable=True),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('source', sa.String(30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_highlights_video_id', 'highlights', ['video_id'])


def downgrade() -> None:
    op.drop_table('highlights')
    op.drop_table('exports')
    op.drop_table('jobs')
    op.drop_table('caption_styles')
    op.drop_table('caption_segments')
    op.drop_table('captions')
    op.drop_table('clips')
    op.drop_table('videos')
