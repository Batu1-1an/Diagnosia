-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing trigger first
DROP TRIGGER IF EXISTS diagnosis_status_change_trigger ON diagnoses;
DROP FUNCTION IF EXISTS log_diagnosis_status_change();

-- Drop existing table and recreate
DROP TABLE IF EXISTS diagnosis_history;

-- Add additional columns to diagnoses table
ALTER TABLE diagnoses
ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS severity TEXT,
ADD COLUMN IF NOT EXISTS follow_up_date DATE,
ADD COLUMN IF NOT EXISTS treatment_duration INTERVAL,
ADD COLUMN IF NOT EXISTS patient_notes TEXT;

-- Create diagnosis_history table for tracking changes
CREATE TABLE diagnosis_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    diagnosis_id UUID NOT NULL,
    changed_by UUID NOT NULL,
    status_from TEXT,
    status_to TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_diagnosis 
        FOREIGN KEY (diagnosis_id) 
        REFERENCES diagnoses(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_changed_by
        FOREIGN KEY (changed_by) 
        REFERENCES profiles(id) 
        ON DELETE CASCADE
);

-- Drop existing indexes if they exist
DROP INDEX IF EXISTS idx_diagnosis_history_diagnosis_id;
DROP INDEX IF EXISTS idx_diagnoses_follow_up_date;
DROP INDEX IF EXISTS idx_diagnoses_completed_at;
DROP INDEX IF EXISTS idx_diagnoses_status;
DROP INDEX IF EXISTS idx_diagnoses_doctor_id;

-- Create indexes for better performance
CREATE INDEX idx_diagnosis_history_diagnosis_id ON diagnosis_history(diagnosis_id);
CREATE INDEX idx_diagnoses_follow_up_date ON diagnoses(follow_up_date);
CREATE INDEX idx_diagnoses_completed_at ON diagnoses(completed_at);
CREATE INDEX idx_diagnoses_status ON diagnoses(status);
CREATE INDEX idx_diagnoses_doctor_id ON diagnoses(doctor_id);

-- Add trigger to track status changes
CREATE FUNCTION log_diagnosis_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE' AND OLD.status IS DISTINCT FROM NEW.status) THEN
        INSERT INTO diagnosis_history (
            diagnosis_id,
            changed_by,
            status_from,
            status_to,
            notes,
            created_at
        ) VALUES (
            NEW.id,
            NEW.doctor_id,
            OLD.status,
            NEW.status,
            NEW.doctor_notes,
            NOW()
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on diagnoses table
CREATE TRIGGER diagnosis_status_change_trigger
    AFTER UPDATE ON diagnoses
    FOR EACH ROW
    EXECUTE FUNCTION log_diagnosis_status_change(); 