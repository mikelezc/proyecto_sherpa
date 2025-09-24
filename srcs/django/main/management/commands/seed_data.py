"""
Django management command to seed the database with sample data.

This command creates sample users, tasks, tags, teams, and related data
for development and testing purposes.
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from authentication.models import CustomUser
from tasks.models import Task, Tag, Team, Comment, TaskHistory, TaskAssignment


class Command(BaseCommand):
    help = 'Seed the database with sample data for development and testing'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)',
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=50,
            help='Number of tasks to create (default: 50)',
        )

    def handle(self, *args, **options):
        """Execute the seed data command."""
        self.stdout.write(
            self.style.SUCCESS('🌱 Starting Task Management System data seeding...')
        )
        
        # Clear existing data if requested
        if options.get('clear', False):
            self.clear_data()
        
        # Create sample data
        users, tasks, tags, teams = self.create_sample_data(
            user_count=options['users'], 
            task_count=options['tasks']
        )
        
        # Print summary
        self.print_summary(users, tasks, tags, teams)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Seed data created successfully!')
        )

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write('🗑️  Clearing existing data...')
        
        # Clear in order to respect foreign key constraints
        Comment.objects.all().delete()
        TaskHistory.objects.all().delete() 
        Task.objects.all().delete()
        Tag.objects.all().delete()
        Team.objects.all().delete()
        
        # Don't delete all users, just non-superusers to preserve admin access
        CustomUser.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.WARNING('Cleared existing data'))

    def create_sample_data(self, user_count=10, task_count=50):
        """Create sample users, tasks, tags, and teams."""
        self.stdout.write('📝 Creating sample data...')
        
        # Create users
        users = self.create_users(user_count)
        
        # Create tags
        tags = self.create_tags()
        
        # Create teams
        teams = self.create_teams(users)
        
        # Create tasks
        tasks = self.create_tasks(users, tags, teams, task_count)
        
        return users, tasks, tags, teams

    def create_users(self, count):
        """Create sample users"""
        self.stdout.write(f'👥 Creating {count} users...')
        
        users = []
        
        # Create a demo admin user (SUPERUSER with full admin access)
        admin_user, created = CustomUser.objects.get_or_create(
            username='demo_admin',
            defaults={
                'email': 'admin@taskmanagement.demo',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('demo123')
            admin_user.save()
            self.stdout.write(f'Created admin user: demo_admin (password: demo123)')
        users.append(admin_user)

        # Create regular users
        for i in range(count):
            username = f'user_{i+1:03d}'
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'user{i+1}@taskmanagement.demo',
                    'first_name': f'User',
                    'last_name': f'{i+1:03d}'
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
            users.append(user)
        
        # Also include any existing users
        all_users = list(CustomUser.objects.all())
        
        self.stdout.write(self.style.SUCCESS(f'Available users: {len(all_users)}'))
        return all_users

    def create_tags(self):
        """Create sample tags"""
        self.stdout.write('🏷️  Creating tags...')
        
        tag_data = [
            ('Frontend', '#3498db'),
            ('Backend', '#e74c3c'), 
            ('Database', '#9b59b6'),
            ('API', '#f39c12'),
            ('Testing', '#2ecc71'),
            ('Documentation', '#95a5a6'),
            ('Bug', '#e67e22'),
            ('Feature', '#1abc9c'),
            ('Urgent', '#c0392b'),
            ('Enhancement', '#8e44ad')
        ]
        
        tags = []
        for name, color in tag_data:
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={'color': color}
            )
            tags.append(tag)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(tags)} tags'))
        return tags

    def create_teams(self, users):
        """Create sample teams"""
        self.stdout.write('👨‍👩‍👧‍👦 Creating teams...')
        
        # Ensure we have at least one user for created_by
        if not users:
            self.stdout.write(self.style.WARNING('No users available for team creation'))
            return []
        
        team_data = [
            ('Development Team', 'Main development team for core features'),
            ('QA Team', 'Quality assurance and testing team'),
            ('DevOps Team', 'Infrastructure and deployment team'),
            ('Design Team', 'UI/UX design and frontend team'),
        ]
        
        teams = []
        for name, description in team_data:
            team, created = Team.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'created_by': users[0]  # Use first user as creator
                }
            )
            
            # Add random users to teams
            if users:
                team_users = random.sample(users, min(random.randint(2, 5), len(users)))
                for user in team_users:
                    team.members.add(user)
            
            teams.append(team)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(teams)} teams'))
        return teams

    def create_tasks(self, users, tags, teams, count):
        """Create sample tasks"""
        self.stdout.write(f'📋 Creating {count} tasks...')
        
        task_templates = [
            'Implement user authentication system',
            'Design responsive dashboard layout',
            'Set up CI/CD pipeline',
            'Write unit tests for API endpoints',
            'Optimize database queries',
            'Create user documentation',
            'Fix login validation bug',
            'Add real-time notifications',
            'Implement task filtering',
            'Set up monitoring system',
            'Refactor legacy code',
            'Add internationalization support',
            'Implement data backup solution',
            'Create admin panel',
            'Add search functionality',
            'Optimize frontend performance',
            'Set up logging system',
            'Implement file upload feature',
            'Add user profile management',
            'Create API documentation'
        ]
        
        statuses = ['TODO', 'IN_PROGRESS', 'DONE']
        priorities = ['LOW', 'MEDIUM', 'HIGH']
        
        tasks = []
        for i in range(count):
            # Select random template or create unique title
            if i < len(task_templates):
                title = task_templates[i]
            else:
                title = f'Task #{i+1}: {random.choice(task_templates)}'
            
            task = Task.objects.create(
                title=title,
                description=f'Detailed description for {title}. This task includes multiple requirements and acceptance criteria.',
                status=random.choice(statuses),
                priority=random.choice(priorities),
                created_by=random.choice(users) if users else None,
                due_date=timezone.now() + timedelta(days=random.randint(1, 30))
            )
            
            # Assign user to task using TaskAssignment
            if users:
                assigned_user = random.choice(users)
                assigned_by = random.choice(users)
                TaskAssignment.objects.create(
                    task=task,
                    user=assigned_user,
                    assigned_by=assigned_by,
                    is_primary=True
                )
            
            # Add random tags
            if tags:
                task_tags = random.sample(tags, random.randint(1, 3))
                for tag in task_tags:
                    task.tags.add(tag)
            
            # Add to random team
            if teams:
                task.team = random.choice(teams)
                task.save()
            
            tasks.append(task)
            
            # Add some comments and history
            self.add_task_interactions(task, users)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(tasks)} tasks'))
        return tasks

    def add_task_interactions(self, task, users):
        """Add comments and history to tasks"""
        if not users:
            return
            
        # Add some comments (random chance)
        if random.random() < 0.3:  # 30% chance
            comment_count = random.randint(1, 3)
            for _ in range(comment_count):
                Comment.objects.create(
                    task=task,
                    author=random.choice(users),
                    content=random.choice([
                        'Working on this task now.',
                        'Need clarification on requirements.',
                        'Making good progress.',
                        'Found an issue, investigating.',
                        'Ready for review.',
                        'Completed the implementation.',
                        'Added tests for this feature.',
                        'Updated documentation.'
                    ])
                )

        # Add some history (random chance)  
        if random.random() < 0.4:  # 40% chance
            history_count = random.randint(1, 2)
            for _ in range(history_count):
                TaskHistory.objects.create(
                    task=task,
                    user=random.choice(users),
                    action=random.choice([
                        'created',
                        'updated',
                        'assigned',
                        'status_changed',
                        'updated',
                        'assigned'
                    ])
                )

    def print_summary(self, users, tasks, tags, teams):
        """Print summary of created data"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 DATA SEEDING SUMMARY'))
        self.stdout.write('='*50)
        self.stdout.write(f'👥 Users: {len(users)}')
        self.stdout.write(f'📋 Tasks: {len(tasks)}')
        self.stdout.write(f'🏷️  Tags: {len(tags)}')
        self.stdout.write(f'👨‍👩‍👧‍👦 Teams: {len(teams)}')
        self.stdout.write('='*50)
        self.stdout.write(self.style.SUCCESS('🎉 Ready for development and testing!'))
        self.stdout.write('\n💡 Login credentials:')
        self.stdout.write('   Admin: demo_admin / demo123')
        self.stdout.write('   Users: user_001 to user_010 / demo123')
