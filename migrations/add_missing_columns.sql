-- Add missing columns to diagnoses table
ALTER TABLE diagnoses
ADD COLUMN IF NOT EXISTS medications JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS diet JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS workout TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS precautions JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS doctor_notes TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Create function to update updated_at timestamp if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at if it doesn't exist
DROP TRIGGER IF EXISTS update_diagnoses_updated_at ON diagnoses;
CREATE TRIGGER update_diagnoses_updated_at
    BEFORE UPDATE ON diagnoses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 