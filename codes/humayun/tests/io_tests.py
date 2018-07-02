from ..src import io_works

print io_works.get_questions_from_file("../dataset/wikipedia.txt")
io_works.put_answers_to_file("humayun/tests/test_answers.txt",["First answer!","Second answer."])
