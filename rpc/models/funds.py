from .db import sa, metadata


Fund = sa.Table(
    't_ff_funds_new',
    metadata,
    sa.Column('secucode', sa.String(12)),
    sa.Column('secuabbr', sa.String(60))
)


Classify = sa.Table(
    't_ff_classify_new',
    metadata,
    sa.Column('secucode_id', sa.ForeignKey('t_ff_funds_new.secucode')),
    sa.Column('branch', sa.String(12)),
    sa.Column('classify', sa.String(20))
)


BasicInfo = sa.Table(
    't_ff_basic_info_new',
    metadata,
    sa.Column('secucode_id', sa.ForeignKey('t_ff_funds_new.secucode')),
    sa.Column('branch', sa.String(12)),
    sa.Column('classify', sa.String(20)),
    sa.Column('maincode', sa.String(12)),
    sa.Column('launch_date', sa.Date()),
    sa.Column('benchmark', sa.String(255)),
    sa.Column('company', sa.String(12))
)


Portfolio = sa.Table(
    't_ff_portfolio',
    metadata,
    sa.Column('port_id', sa.Integer, primary_key=True),
    sa.Column('port_name', sa.String(12)),
    sa.Column('port_type', sa.Integer)
)


PortfolioExpand = sa.Table(
    't_ff_portfolio_expand',
    metadata,
    sa.Column('port_id_id', sa.ForeignKey('t_ff_portfolio.port_id')),
    sa.Column('secucode', sa.String(12)),
    sa.Column('port_type', sa.Integer),
    sa.Column('update_date', sa.Date)
)

