-- Create chat_reviews table
CREATE TABLE IF NOT EXISTS chat_reviews (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    doctor_id UUID REFERENCES profiles(id),
    chat_history JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    doctor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    reviewed_at TIMESTAMPTZ
);

-- Add RLS policies
ALTER TABLE chat_reviews ENABLE ROW LEVEL SECURITY;

-- Policy for users to view their own chat reviews
CREATE POLICY "Users can view their own chat reviews"
    ON chat_reviews FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

-- Policy for users to create their own chat reviews
CREATE POLICY "Users can create their own chat reviews"
    ON chat_reviews FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- Policy for doctors to update reviews assigned to them
CREATE POLICY "Doctors can update assigned reviews"
    ON chat_reviews FOR UPDATE
    TO authenticated
    USING (auth.uid() = doctor_id)
    WITH CHECK (auth.uid() = doctor_id);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS chat_reviews_user_id_idx ON chat_reviews(user_id);
CREATE INDEX IF NOT EXISTS chat_reviews_doctor_id_idx ON chat_reviews(doctor_id);
CREATE INDEX IF NOT EXISTS chat_reviews_status_idx ON chat_reviews(status); 