"""Daily motivational quotes, greetings, and avatar initials helper."""

import datetime
from typing import Tuple

MOTIVATIONAL_QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Dream is not that which you see while sleeping, it is something that does not let you sleep.", "A.P.J. Abdul Kalam"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Nothing in life is to be feared, it is only to be understood. Now is the time to understand more, so that we may fear less.", "Marie Curie"),
    ("We can only see a short distance ahead, but we can see plenty there that needs to be done.", "Alan Turing"),
    ("You have power over your mind — not outside events. Realize this, and you will find strength.", "Marcus Aurelius"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
    ("You may encounter many defeats, but you must not be defeated.", "Maya Angelou"),
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("Action is the foundational key to all success.", "Pablo Picasso"),
    ("Small disciplines repeated with consistency every day lead to great achievements.", "John C. Maxwell"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("Your time is limited, so don't waste it living someone else's life.", "Steve Jobs"),
    ("The best way to predict the future is to create it.", "Peter Drucker"),
    ("Energy and persistence conquer all things.", "Benjamin Franklin"),
    ("Genius is 1% talent and 99% hard work.", "Albert Einstein"),
    ("Doubt kills more dreams than failure ever will.", "Suzy Kassem"),
    ("Focus on being productive instead of busy.", "Tim Ferriss"),
    ("If you want to shine like a sun, first burn like a sun.", "A.P.J. Abdul Kalam"),
    ("Simplicity is the soul of efficiency.", "Austin Freeman"),
    ("Continuous improvement is better than delayed perfection.", "Mark Twain"),
    ("Done is better than perfect.", "Sheryl Sandberg"),
    ("Everything you've ever wanted is sitting on the other side of fear.", "George Addair"),
    ("The mind is everything. What you think you become.", "Buddha"),
    ("Whether you think you can or you think you can't, you're right.", "Henry Ford"),
    ("Discipline is choosing between what you want now and what you want most.", "Abraham Lincoln"),
    ("Opportunities don't happen, you create them.", "Chris Grosser"),
]


def get_daily_motivation() -> Tuple[str, str]:
    """Return a daily rotating motivational quote and its author based on day-of-year."""
    today = datetime.date.today()
    day_idx = today.timetuple().tm_yday
    quote, author = MOTIVATIONAL_QUOTES[day_idx % len(MOTIVATIONAL_QUOTES)]
    return quote, author


def get_greeting(name: str) -> str:
    """Return a time-based greeting for the dashboard hero."""
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return f"Good Morning, {name}"
    elif 12 <= current_hour < 17:
        return f"Good Afternoon, {name}"
    else:
        return f"Good Evening, {name}"


def get_user_initials(name: str) -> str:
    """Generate 2-letter uppercase initials for the profile avatar."""
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    elif parts and len(parts[0]) >= 2:
        return parts[0][:2].upper()
    elif parts:
        return parts[0][:1].upper()
    return "ME"
