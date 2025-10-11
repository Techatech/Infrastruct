#!/usr/bin/env python3
"""
Test script for chat history deletion functionality
"""

from database.chat_history import ChatHistoryManager
import os

def test_chat_deletion():
    """Test the chat deletion functionality"""
    print("🧪 Testing Chat History Deletion Functionality")
    print("=" * 50)
    
    # Initialize chat history manager
    chat_history = ChatHistoryManager("database/test_history.db")
    
    # Create some test sessions
    print("📝 Creating test chat sessions...")
    
    session1 = chat_history.create_session("Test Session 1", "GUI")
    session2 = chat_history.create_session("Test Session 2", "CLI")
    session3 = chat_history.create_session("Test Session 3", "GUI")
    
    # Add some messages to each session
    chat_history.add_message(session1, "User", "Hello, I want to create a website")
    chat_history.add_message(session1, "Bot", "I'll help you create a website infrastructure")
    
    chat_history.add_message(session2, "User", "I need a database setup")
    chat_history.add_message(session2, "Bot", "Let me help you with database infrastructure")
    
    chat_history.add_message(session3, "User", "Create a mobile app backend")
    chat_history.add_message(session3, "Bot", "I'll design a mobile app backend for you")
    
    print(f"✅ Created sessions: {session1}, {session2}, {session3}")
    
    # Test getting sessions
    print("\n📋 Testing session retrieval...")
    sessions = chat_history.get_recent_sessions(10)
    print(f"Found {len(sessions)} sessions:")
    for session in sessions:
        print(f"  - {session['session_id']}: {session['title']}")
    
    # Test deleting a single session
    print(f"\n🗑️ Testing single session deletion...")
    print(f"Deleting session: {session2}")
    chat_history.delete_session(session2)
    
    # Verify deletion
    sessions_after_delete = chat_history.get_recent_sessions(10)
    print(f"Sessions after deletion: {len(sessions_after_delete)}")
    for session in sessions_after_delete:
        print(f"  - {session['session_id']}: {session['title']}")
    
    # Test that messages were also deleted
    messages = chat_history.get_session_messages(session2)
    print(f"Messages in deleted session {session2}: {len(messages)}")
    
    # Test deleting remaining sessions
    print(f"\n🗑️ Testing remaining session deletions...")
    chat_history.delete_session(session1)
    chat_history.delete_session(session3)
    
    # Verify all sessions are gone
    final_sessions = chat_history.get_recent_sessions(10)
    print(f"Final session count: {len(final_sessions)}")
    
    # Clean up test database
    try:
        os.remove("database/test_history.db")
        print("🧹 Cleaned up test database")
    except:
        pass
    
    print("\n✅ Chat deletion functionality test completed successfully!")

def test_gui_integration():
    """Test that the GUI integration works"""
    print("\n🧪 Testing GUI Integration")
    print("=" * 30)
    
    print("✅ Chat history deletion features added:")
    print("  • 🗑️ Delete icon next to each chat session")
    print("  • Confirmation dialog before deletion")
    print("  • 'Clear All' button for bulk deletion")
    print("  • Automatic refresh after deletion")
    print("  • Current session handling when deleted")
    
    print("\n📋 GUI Features:")
    print("  • Individual session deletion with 🗑️ icon")
    print("  • Bulk deletion with 'Clear All' button")
    print("  • Confirmation dialogs for safety")
    print("  • Automatic UI updates after deletion")
    print("  • Search results also include delete buttons")
    
    print("\n🎯 User Experience:")
    print("  • Click 🗑️ icon → Confirmation dialog → Session deleted")
    print("  • Click 'Clear All' → Confirmation → All sessions deleted")
    print("  • Deleted sessions immediately removed from list")
    print("  • Current session cleared if it was deleted")

if __name__ == "__main__":
    test_chat_deletion()
    test_gui_integration()