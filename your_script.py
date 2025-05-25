import json
from django.utils.dateparse import parse_datetime
from enquiry.models import Comment, Enquiry

# Load the new comment structure
with open('comments.json', 'r', encoding='utf-8') as f:
    comments_data = json.load(f)

for mobile, comment_list in comments_data.items():
    try:
        # Get the Enquiry based on mobile number
        enquiry = Enquiry.objects.get(mobile=mobile)

        # Delete old comments for this enquiry
        Comment.objects.filter(enquiry=enquiry).delete()
        print(f"Deleted old comments for enquiry with mobile {mobile}")

        # Create new comments
        for comment_data in comment_list:
            comment_text = comment_data['comment']
            created_at = parse_datetime(comment_data['created_at'])

            Comment.objects.create(
                enquiry=enquiry,
                comment=comment_text,
                created_at=created_at
            )
            print(f"Added comment for {mobile}: {comment_text}")

    except Enquiry.DoesNotExist:
        print(f"Enquiry with mobile {mobile} not found. Skipping...")
    except Exception as e:
        print(f"Error processing comments for {mobile}: {str(e)}")
