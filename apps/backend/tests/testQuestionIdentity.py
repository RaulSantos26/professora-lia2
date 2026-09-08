from app.services.questionIdentityService import normalizeQuestionIds
from app.services.pedagogicalService import PedagogicalService

def test_empty_and_duplicate_ids_are_unique_stable_and_nonmutating():
    for ids in [['',''],['same','same'],[None,None]]:
        source={'questions':[{'questionId':key,'prompt':str(i),'correctAnswer':str(i)} for i,key in enumerate(ids)]}
        fixed=normalizeQuestionIds(source)
        assert [q['questionId'] for q in fixed['questions']]==['lia-q-1','lia-q-2']
        assert fixed==normalizeQuestionIds(fixed)==normalizeQuestionIds(source)
        assert [q['questionId'] for q in source['questions']]==ids

def test_existing_good_ids_and_answers_preserved():
    source={'questions':[{'questionId':'#1','correctAnswer':'A'},{'questionId':'#2','correctAnswer':'B'}]}
    assert normalizeQuestionIds(source) is source

def test_public_questions_match_grading_keys_without_exposing_answers():
    source={'questions':[{'questionId':'','correctAnswer':'A','explanation':'Reason'},{'questionId':'','correctAnswer':'B','explanation':'Reason'}]}
    normalized=normalizeQuestionIds(source)
    public=PedagogicalService.__new__(PedagogicalService)._publicContent('QUIZ',normalized)
    assert [q['questionId'] for q in public['questions']]==[q['questionId'] for q in normalized['questions']]
    assert all('correctAnswer' not in q for q in public['questions'])
