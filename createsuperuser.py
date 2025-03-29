import click
from sqlalchemy.orm import Session
from database import get_db

from utils.auth import get_password_hash
from models.users.users import User, RoleEnum

@click.command()
@click.option('--username', prompt=True, help='The username for the admin user.')
@click.option('--email', prompt=True, help='The email for the admin user.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password for the admin user.')
def create_admin(username, email, password):
    """Create a new admin user."""
    db: Session = next(get_db())
    hashed_password = get_password_hash(password)
    admin = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=RoleEnum.SUPERUSER
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    click.echo(f"Admin user {username} created successfully.")

if __name__ == '__main__':
    create_admin()
