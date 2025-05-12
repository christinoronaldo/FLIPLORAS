import os
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from studio.models import Frame, Video_Final
import shutil
from studio.utils import extract_hd_frames,get_video_duration

class ChatAPIView(APIView):
    def post(self, request):
        temp_path = None
        frames_dir = None

        try:
            video_file = request.FILES.get('video')
            frame_count = int(request.POST.get('frame_count', 120))

            if not video_file:
                return Response({'error': 'No video uploaded'}, status=status.HTTP_400_BAD_REQUEST)

            # Read video data from InMemoryUploadedFile or TemporaryUploadedFile
            video_bytes = video_file.read()

            # Save Template video to disk for FFmpeg processing
            upload_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            temp_path = os.path.join(upload_dir, video_file.name)

            with open(temp_path, 'wb') as f:
                f.write(video_bytes)

            # Get duration from Template file
            duration = get_video_duration(temp_path)

            # Save video directly to database using BinaryField
            video_instance = Video_Final.objects.create(
                title=video_file.name,
                data=video_bytes,
                duration=duration
            )

            # Extract and save frames
            frames_dir = os.path.join(upload_dir, f"{video_file.name}_frames")
            grouped_frames = extract_hd_frames(temp_path, frame_count, frames_dir, video_instance)

            if not grouped_frames:
                return Response({'error': 'No frames extracted'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Encode frames for frontend
            frames = Frame.objects.filter(video=video_instance).order_by('frame_number')
            encoded_frames = [
                {
                    "frame_number": frame.frame_number,
                    "src": f"data:image/png;base64,{base64.b64encode(frame.frame_data).decode('utf-8')}"
                }
                for frame in frames
            ]

            return Response({
                "video_id": video_instance.id,
                "video_title": video_instance.title,
                "frames": encoded_frames
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ Exception:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"🗑️ Deleted temp video: {temp_path}")

            if frames_dir and os.path.exists(frames_dir):
                shutil.rmtree(frames_dir, ignore_errors=True)
                print(f"🧹 Deleted extracted frames directory: {frames_dir}")