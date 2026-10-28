from rest_framework import serializers
from .models import Quiz, Question, AnswerOption, QuizAttempt, QuizResponse, Assignment, AssignmentSubmission, AssignmentGrade

class AnswerOptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'text']

class QuestionPublicSerializer(serializers.ModelSerializer):
    options = AnswerOptionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'position', 'options']

class QuizPublicSerializer(serializers.ModelSerializer):
    questions = QuestionPublicSerializer(many=True, read_only=True)
    total_questions = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'course', 'title', 'description', 'pass_percentage', 'max_attempts', 'time_limit_minutes', 'total_questions', 'questions']

    def get_total_questions(self, obj):
        return obj.questions.count()

class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    pass_percentage = serializers.IntegerField(source='quiz.pass_percentage', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'attempt_number', 'status', 'score', 'passed', 'pass_percentage', 'started_at', 'submitted_at']

class AssignmentGradeSerializer(serializers.ModelSerializer):
    grader_name = serializers.CharField(source='grader_membership.user.full_name', read_only=True)

    class Meta:
        model = AssignmentGrade
        fields = ['id', 'score', 'feedback', 'grader_name', 'graded_at']

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    grade = AssignmentGradeSerializer(read_only=True)
    student_name = serializers.CharField(source='enrollment.student_membership.user.full_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'enrollment', 'version', 'content_text', 'file_url', 'status', 'submitted_at', 'grade', 'student_name']
        read_only_fields = ['id', 'version', 'status', 'submitted_at', 'grade', 'student_name']

class AssignmentDetailSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'course', 'course_title', 'title', 'instructions', 'max_score', 'passing_score', 'due_at', 'is_required', 'created_at']
