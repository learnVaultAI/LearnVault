json_data_roadmap = """
{
"roadmap": {
    "tag" : [" ", " ", " "],
    "course_name": "",
        "description": "",
        "topics": [
        {
            "topic_title": "",
            "sections": [
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
            "topic_title": "",
            "sections": [
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


# json_data_roadmap = """

# {
#   "roadmap": [
#     {
#       "core_category_title": "",
#       "categories": [
#         {
#           "category_title": "",
#           "courses": [
#             {
#               "course_title": "",
#               "description": " ",
#               "tags": [" ", " ", " "],
#               "subtopics": [
#                 {
#                   "topic_title": "Topic Name",
#                   "subtopics": [
#                     "Subtopic 1",
#                     "Subtopic 2",
#                     "...",
#                     "Subtopic n"
#                   ]
#                 }
#               ]
#             }
#           ]
#         }
#       ]
#     }
#   ]
# }

# """


# prompt = """
# You are tasked with creating a learning roadmap for individuals in the position of [{userInput}]. The roadmap should cover essential topics and subtopics to help them excel in their role. Please generate a JSON output outlining the roadmap with detailed topic names, including subtopics where applicable.

# For example, if one of the topics is Communication Skills, include subtopics such as verbal communication, written communication, active listening, empathy, conflict resolution, etc., within the Communication Skills topic.
# add tags which can differentiate {userInput} from other roles.
# provide output in json format. refer to the example below.
# the core_category_title is {core_category_title} and the category_title is {category_title} and the course_name is {userInput}.
# example : {json_data_roadmap}
# """