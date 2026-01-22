from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from patients.models import Patient
from surveys.models import Survey
from llm.inference import generate
from llm.prompt_builder import build_ppc_prompt


class PPCQwenChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        doctor = request.user
        patient_id = request.data.get("patient_id")
        question = request.data.get("question")

        if not patient_id or not question:
            return Response(
                {"error": "patient_id and question are required"},
                status=400
            )

        # ✅ doctor can access ONLY own patients
        patient = get_object_or_404(
            Patient,
            patient_id=patient_id,
            doctor=doctor
        )

        survey = (
            Survey.objects
            .filter(patient=patient)
            .order_by("-created_at")
            .first()
        )

        if not survey:
            return Response(
                {"error": "No survey found for this patient"},
                status=404
            )

        prompt = build_ppc_prompt(
            patient=patient,
            survey=survey,
            section_scores=survey.section_scores.all(),
            answers=survey.answers.all(),
            question=question
        )

        answer = generate(prompt)

        return Response({
            "success": True,
            "patient_id": patient.patient_id,
            "risk_level": survey.risk_level,
            "total_score": survey.total_score,
            "answer": answer
        })
