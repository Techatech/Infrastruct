import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class ChatHistoryManager:
    def __init__(self, db_path: str = "database/infrastruct_history.db"):
        """Initialize the chat history manager with SQLite database"""
        self.db_path = db_path
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create chat sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    interface_type TEXT DEFAULT 'GUI',
                    workflow_state TEXT DEFAULT 'initial',
                    plan_data TEXT,
                    diagram_data TEXT,
                    estimate_data TEXT,
                    template_data TEXT
                )
            ''')
            
            # Create chat messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_type TEXT DEFAULT 'text',
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON chat_messages(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_messages(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_updated ON chat_sessions(updated_at)')
            
            conn.commit()
    
    def create_session(self, title: str, interface_type: str = 'GUI') -> str:
        """Create a new chat session and return session ID"""
        session_id = f"{interface_type.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(title) % 10000}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_sessions (session_id, title, interface_type)
                VALUES (?, ?, ?)
            ''', (session_id, title, interface_type))
            conn.commit()
        
        return session_id
    
    def add_message(self, session_id: str, sender: str, message: str, message_type: str = 'text'):
        """Add a message to the chat session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_messages (session_id, sender, message, message_type)
                VALUES (?, ?, ?, ?)
            ''', (session_id, sender, message, message_type))
            
            # Update session timestamp
            cursor.execute('''
                UPDATE chat_sessions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for a specific session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender, message, timestamp, message_type
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
            ''', (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'sender': row[0],
                    'message': row[1],
                    'timestamp': row[2],
                    'message_type': row[3]
                })
            
            return messages
    
    def get_recent_sessions(self, limit: int = 20) -> List[Dict]:
        """Get recent chat sessions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, title, created_at, updated_at, interface_type, workflow_state
                FROM chat_sessions
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'interface_type': row[4],
                    'workflow_state': row[5]
                })
            
            return sessions
    
    def update_session_data(self, session_id: str, **kwargs):
        """Update session data (plan, diagram, estimate, template)"""
        valid_fields = ['workflow_state', 'plan_data', 'diagram_data', 'estimate_data', 'template_data']
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    
                    cursor.execute(f'''
                        UPDATE chat_sessions 
                        SET {field} = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE session_id = ?
                    ''', (value, session_id))
            
            conn.commit()
    
    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get complete session data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id, title, created_at, updated_at, interface_type, 
                       workflow_state, plan_data, diagram_data, estimate_data, template_data
                FROM chat_sessions
                WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'interface_type': row[4],
                    'workflow_state': row[5],
                    'plan_data': row[6],
                    'diagram_data': row[7],
                    'estimate_data': row[8],
                    'template_data': row[9]
                }
            
            return None
    
    def delete_session(self, session_id: str):
        """Delete a chat session and all its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM chat_sessions WHERE session_id = ?', (session_id,))
            conn.commit()
    
    def get_session_template_info(self, session_id: str) -> Optional[Dict]:
        """Get template information for a session to help with cleanup"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, template_data
                FROM chat_sessions
                WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'title': row[0],
                    'template_data': row[1]
                }
            
            return None
    
    def search_sessions(self, query: str, limit: int = 10) -> List[Dict]:
        """Search sessions by title or message content"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT s.session_id, s.title, s.created_at, s.updated_at, s.interface_type
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON s.session_id = m.session_id
                WHERE s.title LIKE ? OR m.message LIKE ?
                ORDER BY s.updated_at DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'interface_type': row[4]
                })
            
            return sessions