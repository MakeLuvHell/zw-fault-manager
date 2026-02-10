-- Name: wxsafe_fz_log; Type: TABLE; Schema: wxsafe; Owner: -
CREATE TABLE IF NOT EXISTS wxsafe.wxsafe_fz_log (
    id BIGSERIAL PRIMARY KEY,
    clue_number VARCHAR(100) NOT NULL,
    operator_id VARCHAR(50),
    operator_name VARCHAR(100),
    action_type VARCHAR(20) DEFAULT 'UPDATE',
    change_diff JSONB,
    created_time TIMESTAMP DEFAULT NOW()
);

-- Name: idx_wxsafe_log_clue_number; Type: INDEX; Schema: wxsafe; Owner: -
CREATE INDEX IF NOT EXISTS idx_wxsafe_log_clue_number ON wxsafe.wxsafe_fz_log(clue_number);

COMMENT ON TABLE wxsafe.wxsafe_fz_log IS '涉诈信息操作日志表';
COMMENT ON COLUMN wxsafe.wxsafe_fz_log.clue_number IS '关联线索编号';
COMMENT ON COLUMN wxsafe.wxsafe_fz_log.change_diff IS '变更差异快照';
