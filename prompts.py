json_data_roadmap = """
{
"roadmap": {
    "tag" : [" ", " ", " "],
    "title": "",
        "description": "",
        "topics": [
        {
            "title": "",
            "subtopics": [
            {
                "topic": "topic_name_1",
                "subtopics": [
                "sub_topic_1",
                "sub_topic_2",
                "...",
                "sub_topic_n"
                ]
            },
            {
                "topic": "topic_name_n",
                "subtopics": [
                "sub_topic_1",
                "sub_topic_2",
                "...",
                "sub_topic_n"
                ]
            }
            ]
        },

        {
            "title": "",
            "subtopics": [
            {
                "topic": "topic_name_1",
                "subtopics": [
                "sub_topic_1",
                "sub_topic_2",
                "...",
                "sub_topic_n"
                ]
            },
            {
                "topic": "topic_name_n",
                "subtopics": [
                "sub_topic_1",
                "sub_topic_2",
                "...",
                "sub_topic_n"
                ]
            }
            ]
        }
        ]
    }
    }

    """
prompt = """
You are tasked with creating a learning roadmap for individuals in the position of [{userInput}]. The roadmap should cover essential topics and subtopics to help them excel in their role. Please generate a JSON output outlining the roadmap with detailed topic names, including subtopics where applicable.

For example, if one of the topics is Communication Skills, include subtopics such as verbal communication, written communication, active listening, empathy, conflict resolution, etc., within the Communication Skills topic.
add tags which can differentiate {userInput} from other roles
provide output in json format. refer to the example below.
example : {json_data_roadmap}
"""