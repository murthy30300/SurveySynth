import csv

def extract_feedback_from_csv(filepath, feedback_column='feedback'):
    responses = []
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if feedback_column in row:
                responses.append(row[feedback_column])
    return responses
# if __name__ == "__main__":
#     feedback = extract_feedback_from_csv("SurveySynth/src/test-data/sample-survey.csv")
#     for i, line in enumerate(feedback):
#         print(f"{i+1}. {line}")
