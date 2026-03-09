def ai_generation_context(request):
    """Add AI generation course ID to context for dashboard floating widget"""
    if request.path.startswith('/dashboard/'):
        return {
            'ai_generating_course_id': request.session.get('ai_generating_course_id'),
            'ai_generating_course_name': request.session.get('ai_generating_course_name', ''),
        }
    return {}
