"""Stable question keys shared by publication and grading, including legacy content."""
def normalizeQuestionIds(content):
    if not isinstance(content, dict): return content
    questions = content.get('questions')
    if not isinstance(questions, list) or not all(isinstance(q, dict) for q in questions): return content
    identifiers = [q.get('questionId') for q in questions]
    if all(isinstance(key, str) and key.strip() for key in identifiers) and len(set(identifiers)) == len(identifiers):
        return content
    return {**content, 'questions': [{**question, 'questionId': f'lia-q-{index + 1}'} for index, question in enumerate(questions)]}
