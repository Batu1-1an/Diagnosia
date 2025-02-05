-- Fix JSONB arrays in diagnoses table
UPDATE diagnoses 
SET 
    medications = CASE 
        WHEN medications IS NULL THEN '[]'::jsonb
        WHEN medications::text = '[]' THEN '[]'::jsonb
        WHEN medications::text LIKE '[%]' THEN medications::text::jsonb
        ELSE jsonb_build_array(medications)
    END,
    diet = CASE 
        WHEN diet IS NULL THEN '[]'::jsonb
        WHEN diet::text = '[]' THEN '[]'::jsonb
        WHEN diet::text LIKE '[%]' THEN diet::text::jsonb
        ELSE jsonb_build_array(diet)
    END,
    precautions = CASE 
        WHEN precautions IS NULL THEN '[]'::jsonb
        WHEN precautions::text = '[]' THEN '[]'::jsonb
        WHEN precautions::text LIKE '[%]' THEN precautions::text::jsonb
        ELSE jsonb_build_array(precautions)
    END,
    symptoms = CASE 
        WHEN symptoms IS NULL THEN '[]'::jsonb
        WHEN symptoms::text = '[]' THEN '[]'::jsonb
        WHEN symptoms::text LIKE '[%]' THEN symptoms::text::jsonb
        ELSE jsonb_build_array(symptoms)
    END
WHERE 
    medications IS NULL 
    OR medications::text = '[]'
    OR diet IS NULL 
    OR diet::text = '[]'
    OR precautions IS NULL 
    OR precautions::text = '[]'
    OR symptoms IS NULL 
    OR symptoms::text = '[]'; 