import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_video_chunk_logic(form, files):
    """
    Saves a video chunk sent from the frontend into a session-specific folder.
    """
    try:
        video_file = files.get('video')
        question_id = form.get('question_id')
        session_id = form.get('session_id')

        # 1. Validate inputs (Returns dict, 400 Bad Request)
        if not all([video_file, question_id, session_id]):
            return {"error": "Missing video, question_id, or session_id"}, 400

        # 2. Define where these videos will live
        base_upload_dir = os.path.join(current_app.root_path, "uploads", "sessions", str(session_id))
        
        # Ensure the directory exists
        os.makedirs(base_upload_dir, exist_ok=True)

        # 3. Sanitize the filename
        safe_filename = secure_filename(video_file.filename)
        if not safe_filename:
            safe_filename = f"q_{question_id}.webm"
            
        file_path = os.path.join(base_upload_dir, safe_filename)

        # 4. Save the file to the disk
        video_file.save(file_path)

        print(f"\n[💾] Saved Video Chunk:")
        print(f"     Session  : {session_id}")
        print(f"     Question : {question_id}")
        print(f"     Location : {file_path}\n")

        # ---------------------------------------------------------
        # 🤖 ML INTEGRATION POINT:
        # Later, you can import and trigger your ML analysis here.
        # ---------------------------------------------------------

        # 5. Return success (Returns dict, 201 Created)
        return {
            "status": "success",
            "message": "Video chunk saved successfully.",
            "file_path": file_path,
            "question_id": question_id
        }, 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to save video: {str(e)}"}, 500