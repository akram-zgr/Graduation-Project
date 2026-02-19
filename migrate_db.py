"""
Database migration script to add role field to existing users
and department_id to knowledge_base.

This script safely updates the database schema without losing data.
"""
from app import app, db
from models.user import User
from models.knowledge_base import KnowledgeBase
from sqlalchemy import text


def migrate_database():
    """Migrate database to add new fields"""
    with app.app_context():
        print("=" * 70)
        print("DATABASE MIGRATION - Multi-University Role System")
        print("=" * 70)
        print()
        
        # Check if migration is needed
        try:
            # Try to query role column
            db.session.execute(text("SELECT role FROM users LIMIT 1"))
            print("✓ Role column already exists in users table")
            role_exists = True
        except Exception:
            print("→ Role column needs to be added to users table")
            role_exists = False
        
        try:
            # Try to query department_id column in knowledge_base
            db.session.execute(text("SELECT department_id FROM knowledge_base LIMIT 1"))
            print("✓ Department_id column already exists in knowledge_base table")
            dept_kb_exists = True
        except Exception:
            print("→ Department_id column needs to be added to knowledge_base table")
            dept_kb_exists = False
        
        print()
        
        # Perform migrations if needed
        if not role_exists:
            print("Adding role column to users table...")
            try:
                db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'student'"))
                db.session.commit()
                print("✓ Role column added successfully")
                
                # Update existing users based on is_admin and university_id
                print("Migrating existing user roles...")
                
                # Super admins: is_admin=True and no university
                db.session.execute(text(
                    "UPDATE users SET role = 'super_admin' WHERE is_admin = 1 AND university_id IS NULL"
                ))
                
                # University admins: is_admin=True and has university
                db.session.execute(text(
                    "UPDATE users SET role = 'university_admin' WHERE is_admin = 1 AND university_id IS NOT NULL"
                ))
                
                # Students: is_admin=False
                db.session.execute(text(
                    "UPDATE users SET role = 'student' WHERE is_admin = 0 OR is_admin IS NULL"
                ))
                
                db.session.commit()
                print("✓ Existing users migrated successfully")
                
            except Exception as e:
                db.session.rollback()
                print(f"✗ Error adding role column: {e}")
                return False
        
        if not dept_kb_exists:
            print("\nAdding department_id column to knowledge_base table...")
            try:
                db.session.execute(text(
                    "ALTER TABLE knowledge_base ADD COLUMN department_id INTEGER REFERENCES departments(id)"
                ))
                db.session.commit()
                print("✓ Department_id column added successfully")
            except Exception as e:
                db.session.rollback()
                print(f"✗ Error adding department_id column: {e}")
                return False
        
        print()
        print("=" * 70)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()
        
        # Display migration summary
        print("Summary:")
        print(f"  Total users: {User.query.count()}")
        print(f"  Super admins: {User.query.filter_by(role='super_admin').count()}")
        print(f"  University admins: {User.query.filter_by(role='university_admin').count()}")
        print(f"  Students: {User.query.filter_by(role='student').count()}")
        print(f"  Knowledge base entries: {KnowledgeBase.query.count()}")
        print()
        
        return True


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("MULTI-UNIVERSITY ROLE SYSTEM - DATABASE MIGRATION")
    print("=" * 70)
    print()
    print("This script will:")
    print("  1. Add 'role' column to users table")
    print("  2. Add 'department_id' column to knowledge_base table")
    print("  3. Migrate existing user roles based on is_admin flag")
    print()
    
    response = input("Continue with migration? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print()
        success = migrate_database()
        if success:
            print("\n✓ Database migration completed successfully!")
            print("  You can now use the enhanced multi-university role system.")
        else:
            print("\n✗ Migration failed. Please check the errors above.")
    else:
        print("\nMigration cancelled.")
