# -*- coding: utf-8 -*-
import codecs
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_questions_from_file(questions_filepath):
    questions = []
    with codecs.open(questions_filepath, 'r', 'UTF-8') as f:
        for line in f.read().splitlines():
            questions.append(line)
    logger.debug(str(len(questions))+" questions added from file.")
    return questions

def put_answers_to_file(answers_filepath, answers):
    output_file = codecs.open(answers_filepath, 'w', 'utf-8')
    for answer in answers:
        output_file.write(answer)
        output_file.write('\n')
    logger.debug(str(len(answers))+" answers added to file.")
    output_file.close()

