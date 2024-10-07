# Database Schema

Our application uses MongoDB with the following collections:

## Courses Collection
000json
{
  "_id": ObjectId,
  "title": String,
  "slug": String,
  "description": String,
  "category": String,
  "tags": [String],
  "level": String,
  "instructor_id": ObjectId,
  "topics": [
    {
      "topic_title": String,
      "sections": [
        {
          "topic": String, // Subtopic title
          "subtopics": [String],
          "videos": [ObjectId] // References to Content collection
        }
      ]
    }
  ],
  "requirements": [String],
  "outcomes": [String],
  "rating": {
    "average": Number,
    "count": Number
  },
  "enrollment_count": Number,
  "price": {
    "amount": Number,
    "currency": String
  },
  "created_at": Date,
  "updated_at": Date,
  "status": String // draft, published, archived
}
000

## Content Collection
000json
{
  "_id": ObjectId,
  "course_id": ObjectId,
  "type": String, // video, quiz, assignment, etc.
  "title": String,
  "description": String,
  "order": Number,
  "metadata": {
    "duration": Number, // for videos
    "file_url": String,
    "thumbnail_url": String,
    "views": String
  },
  "transcript": String,
  "captions": [
    {
      "language": String,
      "file_url": String
    }
  ],
  "quiz_data": { // if type is quiz
    "questions": [
      {
        "question": String,
        "options": [String],
        "correct_answer": Number
      }
    ]
  },
  "assignment_data": { // if type is assignment
    "instructions": String,
    "due_date": Date,
    "submission_type": String
  },
  "created_at": Date,
  "updated_at": Date
}
000

## Users Collection
000json
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password_hash": String,
  "role": String, // student, instructor, admin
  "profile": {
    "full_name": String,
    "bio": String,
    "avatar_url": String
  },
  "created_at": Date,
  "updated_at": Date
}
000

## Enrollments Collection
000json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "course_id": ObjectId,
  "enrolled_at": Date,
  "completed_at": Date,
  "progress": Number, // percentage
  "last_accessed": Date
}
000

## Progress Collection
000json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "course_id": ObjectId,
  "content_id": ObjectId,
  "status": String, // started, completed
  "progress": Number, // for videos
  "quiz_score": Number, // for quizzes
  "updated_at": Date
}
000

## Reviews Collection
000json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "course_id": ObjectId,
  "rating": Number,
  "review_text": String,
  "created_at": Date,
  "updated_at": Date
}
000

## Additional Features:

### Discussion Forums Collection
000json
{
  "_id": ObjectId,
  "course_id": ObjectId,
  "title": String,
  "description": String,
  "created_by": ObjectId, // user_id
  "created_at": Date,
  "updated_at": Date
}
000

### Forum Posts Collection
000json
{
  "_id": ObjectId,
  "forum_id": ObjectId,
  "user_id": ObjectId,
  "content": String,
  "created_at": Date,
  "updated_at": Date,
  "parent_post_id": ObjectId // for replies
}
000

### Notifications Collection
000json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "type": String, // e.g., "new_message", "course_update"
  "content": String,
  "read": Boolean,
  "created_at": Date
}
000

### Certificates Collection
000json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "course_id": ObjectId,
  "issued_at": Date,
  "certificate_url": String
}
000