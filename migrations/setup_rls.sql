-- Drop existing policies first
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Users can view their own diagnoses" ON diagnoses;
DROP POLICY IF EXISTS "Users can create their own diagnoses" ON diagnoses;
DROP POLICY IF EXISTS "Doctors can update diagnoses" ON diagnoses;

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE diagnoses ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Public profiles are viewable by everyone"
    ON profiles 
    FOR SELECT
    USING (true);

CREATE POLICY "Users can update own profile"
    ON profiles 
    FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON profiles 
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Diagnoses policies
CREATE POLICY "Users can view their own diagnoses"
    ON diagnoses 
    FOR SELECT
    USING (
        auth.uid() = user_id OR
        EXISTS (
            SELECT 1 
            FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'doctor' 
            AND profiles.is_verified = true
        )
    );

CREATE POLICY "Users can create their own diagnoses"
    ON diagnoses 
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Doctors can update diagnoses"
    ON diagnoses 
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 
            FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'doctor' 
            AND profiles.is_verified = true
        )
    );

-- Chat Reviews RLS
DROP POLICY IF EXISTS "Users can view their own chat reviews" ON chat_reviews;
DROP POLICY IF EXISTS "Users can create their own chat reviews" ON chat_reviews;
DROP POLICY IF EXISTS "Doctors can view assigned chat reviews" ON chat_reviews;
DROP POLICY IF EXISTS "Doctors can update assigned reviews" ON chat_reviews;

ALTER TABLE chat_reviews ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own chat reviews"
    ON chat_reviews 
    FOR SELECT
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create their own chat reviews"
    ON chat_reviews 
    FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Doctors can view assigned chat reviews"
    ON chat_reviews 
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 
            FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'doctor'
            AND profiles.is_verified = true
        )
    );

CREATE POLICY "Doctors can update assigned reviews"
    ON chat_reviews 
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 
            FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'doctor'
            AND profiles.is_verified = true
        )
    );

-- Grant necessary permissions
GRANT ALL ON profiles TO authenticated;
GRANT ALL ON diagnoses TO authenticated;
GRANT ALL ON chat_reviews TO authenticated; 