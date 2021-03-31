from .db import sa, metadata


Classify = sa.Table(
    't_ff_classify_new',
    metadata,
    sa.Column('windcode_id', sa.String(12)),
    sa.Column('branch', sa.String(12)),
    sa.Column('classify', sa.String(20))
)
