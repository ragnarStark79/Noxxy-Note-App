// Noxxy Frontend JavaScript - Apple Notes Style
// Handles all API interactions and DOM updates

const API_BASE = '/api';
let currentFolderId = null;
let currentNoteId = null;
let notesData = [];
let autoSaveTimeout = null;
let isEditing = false;

// ========== Utility Functions ==========

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== API Functions ==========

async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(API_BASE + endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// ========== Notes API ==========

async function createNote(noteData) {
    const data = await apiRequest('/notes', {
        method: 'POST',
        body: JSON.stringify(noteData)
    });
    showToast(data.message || 'Note created successfully');
    return data.data;
}

async function updateNoteAPI(noteId, noteData) {
    const data = await apiRequest(`/notes/${noteId}`, {
        method: 'PUT',
        body: JSON.stringify(noteData)
    });
    return data.data;
}

async function deleteNote(noteId) {
    const data = await apiRequest(`/notes/${noteId}`, {
        method: 'DELETE'
    });
    showToast(data.message || 'Note moved to bin');
    return true;
}

async function togglePinNote(noteId) {
    const data = await apiRequest(`/notes/${noteId}/pin`, {
        method: 'PATCH'
    });
    return data.data;
}

async function listNotes(folderId = null) {
    const url = folderId ? `/notes?folder_id=${folderId}` : '/notes';
    const data = await apiRequest(url);
    return data.data;
}

// ========== Bin API ==========

async function listBin() {
    const data = await apiRequest('/bin');
    return data.data;
}

async function restoreNote(noteId) {
    const data = await apiRequest(`/bin/${noteId}/restore`, {
        method: 'PATCH'
    });
    showToast(data.message || 'Note restored');
    return data.data;
}

async function deletePermanently(noteId) {
    if (!confirm('Permanently delete this note? This cannot be undone!')) {
        return false;
    }
    const data = await apiRequest(`/bin/${noteId}`, {
        method: 'DELETE'
    });
    showToast(data.message || 'Note deleted permanently');
    return true;
}

// ========== Folders API ==========

async function createFolder(name) {
    const data = await apiRequest('/folders', {
        method: 'POST',
        body: JSON.stringify({ name })
    });
    showToast(data.message || 'Folder created');
    return data.data;
}

async function listFolders() {
    const data = await apiRequest('/folders');
    return data.data;
}

async function deleteFolder(folderId) {
    if (!confirm('Delete this folder? Notes will not be deleted.')) {
        return false;
    }
    const data = await apiRequest(`/folders/${folderId}?remove_notes=true`, {
        method: 'DELETE'
    });
    showToast(data.message || 'Folder deleted');
    return true;
}

// ========== DOM Rendering ==========

function renderNoteListItem(note) {
    const li = document.createElement('li');
    li.className = `note-item-compact ${note.is_pinned ? 'pinned' : ''} ${currentNoteId === note.id ? 'active' : ''}`;
    li.dataset.noteId = note.id;

    const preview = note.content ? note.content.substring(0, 60) + (note.content.length > 60 ? '...' : '') : 'No content';

    li.innerHTML = `
        <div class="note-item-header">
            <div class="note-item-title">
                ${escapeHtml(note.title)}
            </div>
            <div class="note-item-actions">
                <button class="pin-btn ${note.is_pinned ? 'pinned' : ''}" 
                        onclick="event.stopPropagation(); handlePinToggle('${note.id}')" 
                        title="${note.is_pinned ? 'Unpin' : 'Pin'}">
                    ${note.is_pinned ? '📌' : '📍'}
                </button>
                <button class="delete-btn" 
                        onclick="event.stopPropagation(); handleDelete('${note.id}')" 
                        title="Delete">
                    🗑️
                </button>
            </div>
        </div>
        <div class="note-item-preview">${escapeHtml(preview)}</div>
        <div class="note-item-meta">${formatDate(note.created_at)}</div>
    `;

    li.onclick = () => selectNote(note.id);

    return li;
}

function renderEditableNoteDetail(note) {
    const detailContainer = document.getElementById('note-detail-content');
    detailContainer.className = 'note-detail-editing';

    detailContainer.innerHTML = `
        <div class="note-header">
            <input type="text" id="note-title" value="${escapeHtml(note.title)}" placeholder="Note Title" />
            <div class="note-header-actions">
                <button class="btn btn-sm btn-primary" onclick="saveCurrentNote()">💾 Save</button>
            </div>
        </div>
        <div class="note-content">
            <textarea id="note-content" placeholder="Start writing...">${escapeHtml(note.content || '')}</textarea>
        </div>
        <div class="note-actions">
            <span class="save-status" id="save-status"></span>
        </div>
    `;

    // Setup auto-save on input
    const titleInput = document.getElementById('note-title');
    const contentInput = document.getElementById('note-content');

    titleInput.addEventListener('input', () => scheduleAutoSave());
    contentInput.addEventListener('input', () => scheduleAutoSave());
}

function renderBinNoteDetail(note) {
    const detailContainer = document.getElementById('note-detail-content');
    detailContainer.className = 'note-detail-viewing';

    detailContainer.innerHTML = `
        <div class="note-header">
            <h1>${escapeHtml(note.title)}</h1>
            <div class="note-header-actions">
                <button class="btn btn-sm btn-success" onclick="handleRestore('${note.id}')">
                    ♻️ Restore
                </button>
                <button class="btn btn-sm btn-danger" onclick="handleDeletePermanent('${note.id}')">
                    ❌ Delete Forever
                </button>
            </div>
        </div>
        <div class="note-content">
            <div style="white-space: pre-wrap; line-height: 1.6;">${escapeHtml(note.content || '')}</div>
        </div>
    `;
}

function renderFolder(folder) {
    const li = document.createElement('li');
    li.className = `folder-item ${currentFolderId === folder.id ? 'active' : ''}`;
    li.dataset.folderId = folder.id;

    li.innerHTML = `
        <div class="folder-item-content" onclick="selectFolder('${folder.id}')">
            <span>📁 ${escapeHtml(folder.name)}</span>
        </div>
        <span class="folder-count">${folder.note_count || 0}</span>
        <div class="folder-item-actions">
            <button onclick="event.stopPropagation(); handleFolderDelete('${folder.id}')" title="Delete folder">
                🗑️
            </button>
        </div>
    `;

    return li;
}

// ========== Auto-Save Functionality ==========

function scheduleAutoSave() {
    const saveStatus = document.getElementById('save-status');
    if (saveStatus) {
        saveStatus.textContent = 'Unsaved changes...';
        saveStatus.className = 'save-status';
    }

    if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
    }

    autoSaveTimeout = setTimeout(() => {
        saveCurrentNote(true);
    }, 2000); // Auto-save after 2 seconds of inactivity
}

async function saveCurrentNote(isAutoSave = false) {
    if (!currentNoteId) return;

    const titleInput = document.getElementById('note-title');
    const contentInput = document.getElementById('note-content');
    const saveStatus = document.getElementById('save-status');

    if (!titleInput || !contentInput) return;

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();

    if (!title) {
        showToast('Title is required', 'error');
        return;
    }

    try {
        if (saveStatus) {
            saveStatus.textContent = 'Saving...';
            saveStatus.className = 'save-status saving';
        }

        await updateNoteAPI(currentNoteId, { title, content });

        if (saveStatus) {
            saveStatus.textContent = isAutoSave ? '✓ Auto-saved' : '✓ Saved';
            saveStatus.className = 'save-status saved';
        }

        if (!isAutoSave) {
            showToast('Note saved successfully');
        }

        // Refresh the notes list to show updated title/content
        await loadNotes();
    } catch (error) {
        if (saveStatus) {
            saveStatus.textContent = '✗ Save failed';
            saveStatus.className = 'save-status';
        }
    }
}

// ========== Event Handlers ==========

async function handleCreateNote(event) {
    event.preventDefault();

    const form = event.target;
    const title = form.title.value.trim();
    const content = form.content.value.trim();
    const folderId = form.folder_id.value || null;

    if (!title) {
        showToast('Title is required', 'error');
        return;
    }

    try {
        await createNote({ title, content, folder_id: folderId });
        form.reset();
        hideCreateNoteModal();
        loadNotes();
        loadFolders();
    } catch (error) {
        // Error already shown
    }
}

async function handlePinToggle(noteId) {
    try {
        await togglePinNote(noteId);
        loadNotes();
    } catch (error) {
        // Error already shown
    }
}

async function handleDelete(noteId) {
    try {
        await deleteNote(noteId);
        if (currentNoteId === noteId) {
            currentNoteId = null;
            showEmptyNoteDetail();
        }
        loadNotes();
        loadFolders();
    } catch (error) {
        // Error already shown
    }
}

async function handleRestore(noteId) {
    try {
        await restoreNote(noteId);
        currentNoteId = null;
        loadBin();
        showEmptyNoteDetail();
    } catch (error) {
        // Error already shown
    }
}

async function handleDeletePermanent(noteId) {
    try {
        const deleted = await deletePermanently(noteId);
        if (deleted) {
            currentNoteId = null;
            loadBin();
            showEmptyNoteDetail();
        }
    } catch (error) {
        // Error already shown
    }
}

async function handleCreateFolder(event) {
    event.preventDefault();

    const form = event.target;
    const name = form.folder_name.value.trim();

    if (!name) {
        showToast('Folder name is required', 'error');
        return;
    }

    try {
        await createFolder(name);
        form.reset();
        loadFolders();
    } catch (error) {
        // Error already shown
    }
}

async function handleFolderDelete(folderId) {
    try {
        const deleted = await deleteFolder(folderId);
        if (deleted) {
            if (currentFolderId === folderId) {
                currentFolderId = null;
            }
            loadFolders();
            loadNotes();
        }
    } catch (error) {
        // Error already shown
    }
}

function selectNote(noteId) {
    currentNoteId = noteId;
    const note = notesData.find(n => n.id === noteId);

    if (note) {
        // Update active state in list
        document.querySelectorAll('.note-item-compact').forEach(item => {
            item.classList.toggle('active', item.dataset.noteId === noteId);
        });

        // Render editable note detail
        if (window.location.pathname === '/bin') {
            renderBinNoteDetail(note);
        } else {
            renderEditableNoteDetail(note);
        }
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            closeSidebars();
        }
    }
}

function selectFolder(folderId) {
    // Update currentFolderId
    currentFolderId = folderId;
    
    // Update active state for all folder items
    const allNotesFolder = document.getElementById('all-notes-folder');
    const customFolders = document.querySelectorAll('.folder-item[data-folder-id]');
    
    if (allNotesFolder) {
        if (folderId === null) {
            allNotesFolder.classList.add('active');
        } else {
            allNotesFolder.classList.remove('active');
        }
    }
    
    customFolders.forEach(folder => {
        if (folder.dataset.folderId === folderId) {
            folder.classList.add('active');
        } else {
            folder.classList.remove('active');
        }
    });
    
    // Load notes for the selected folder
    loadNotes();
}

function showEmptyNoteDetail() {
    const detailContainer = document.getElementById('note-detail-content');
    detailContainer.className = 'note-detail-empty';
    
    if (window.location.pathname === '/bin') {
        detailContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🗑️</div>
                <h3>Deleted Notes</h3>
                <p>Select a note to restore or permanently delete</p>
            </div>
        `;
    } else {
        detailContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <h3>Select a note</h3>
                <p>Choose a note from the list or create a new one</p>
            </div>
        `;
    }
}

// ========== Modal Functions ==========

function showCreateNoteModal() {
    const modal = document.getElementById('create-note-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function hideCreateNoteModal() {
    const modal = document.getElementById('create-note-modal');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('note-form').reset();
    }
}

// ========== Data Loading ==========

async function loadNotes() {
    showLoading('notes-list');

    try {
        notesData = await listNotes(currentFolderId);
        const notesList = document.getElementById('notes-list');

        if (!notesList) return;

        if (notesData.length === 0) {
            notesList.innerHTML = `
                <div class="empty-state" style="padding: 40px 20px;">
                    <div class="empty-state-icon" style="font-size: 48px;">📝</div>
                    <h3 style="font-size: 16px;">No notes yet</h3>
                    <p style="font-size: 14px;">Create your first note!</p>
                </div>
            `;
            
            // Update "All Notes" count
            if (currentFolderId === null) {
                const allNotesCount = document.getElementById('all-notes-count');
                if (allNotesCount) {
                    allNotesCount.textContent = '0';
                }
            }
            return;
        }

        notesList.innerHTML = '';
        notesData.forEach(note => {
            const noteElement = renderNoteListItem(note);
            notesList.appendChild(noteElement);
        });
        
        // Update "All Notes" count when viewing all notes
        if (currentFolderId === null) {
            const allNotesCount = document.getElementById('all-notes-count');
            if (allNotesCount) {
                allNotesCount.textContent = notesData.length;
            }
        }

        // Re-select current note if it exists
        if (currentNoteId) {
            const stillExists = notesData.find(n => n.id === currentNoteId);
            if (stillExists) {
                selectNote(currentNoteId);
            } else {
                currentNoteId = null;
                showEmptyNoteDetail();
            }
        } else if (notesData.length > 0) {
            // Auto-select first note if none selected
            selectNote(notesData[0].id);
        }
    } catch (error) {
        document.getElementById('notes-list').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Failed to load notes</h3>
                <p style="font-size: 13px;">${error.message}</p>
            </div>
        `;
    }
}

async function loadBin() {
    showLoading('bin-list');

    try {
        notesData = await listBin();
        const binList = document.getElementById('bin-list');

        if (!binList) return;

        if (notesData.length === 0) {
            binList.innerHTML = `
                <div class="empty-state" style="padding: 40px 20px;">
                    <div class="empty-state-icon" style="font-size: 48px;">🗑️</div>
                    <h3 style="font-size: 16px;">Bin is empty</h3>
                    <p style="font-size: 14px;">Deleted notes will appear here</p>
                </div>
            `;
            return;
        }

        binList.innerHTML = '';
        notesData.forEach(note => {
            const noteElement = renderNoteListItem(note);
            binList.appendChild(noteElement);
        });

        // Select first note if none selected
        if (!currentNoteId && notesData.length > 0) {
            selectNote(notesData[0].id);
        }
    } catch (error) {
        document.getElementById('bin-list').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Failed to load bin</h3>
                <p style="font-size: 13px;">${error.message}</p>
            </div>
        `;
    }
}

async function loadFolders() {
    try {
        const folders = await listFolders();
        const folderList = document.getElementById('folder-list');
        const folderSelect = document.getElementById('folder-select');

        if (folderList) {
            // Get the "All Notes" folder element (keep it in place)
            const allNotesFolder = document.getElementById('all-notes-folder');
            
            // Clear only custom folders (not the "All Notes" folder)
            const customFolders = folderList.querySelectorAll('.folder-item[data-folder-id]');
            customFolders.forEach(folder => folder.remove());
            
            // Append custom folders after "All Notes"
            folders.forEach(folder => {
                const folderElement = renderFolder(folder);
                folderList.appendChild(folderElement);
            });
            
            // Update "All Notes" count with total notes
            const allNotesCount = document.getElementById('all-notes-count');
            if (allNotesCount) {
                const totalNotes = folders.reduce((sum, folder) => sum + (folder.note_count || 0), 0);
                // Note: This shows notes in folders. We'll update it when notes load.
                allNotesCount.textContent = totalNotes;
            }
        }

        if (folderSelect) {
            folderSelect.innerHTML = '<option value="">No Folder</option>';
            folders.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder.id;
                option.textContent = folder.name;
                folderSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load folders:', error);
    }
}

// ========== Initialize ==========

// Mobile Sidebar Toggle Functions
function toggleLeftSidebar() {
    const sidebar = document.getElementById('notes-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const btn = document.getElementById('left-menu-btn');
    
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
    btn.classList.toggle('active');
    
    // Close right sidebar if open
    const rightSidebar = document.getElementById('right-sidebar');
    const rightBtn = document.getElementById('right-menu-btn');
    if (rightSidebar.classList.contains('open')) {
        rightSidebar.classList.remove('open');
        rightBtn.classList.remove('active');
    }
    
    // Toggle body scroll
    if (sidebar.classList.contains('open')) {
        document.body.classList.add('no-scroll');
    } else {
        document.body.classList.remove('no-scroll');
    }
}

function toggleRightSidebar() {
    const sidebar = document.getElementById('right-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const btn = document.getElementById('right-menu-btn');
    
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
    btn.classList.toggle('active');
    
    // Close left sidebar if open
    const leftSidebar = document.getElementById('notes-sidebar');
    const leftBtn = document.getElementById('left-menu-btn');
    if (leftSidebar.classList.contains('open')) {
        leftSidebar.classList.remove('open');
        leftBtn.classList.remove('active');
    }
    
    // Toggle body scroll
    if (sidebar.classList.contains('open')) {
        document.body.classList.add('no-scroll');
    } else {
        document.body.classList.remove('no-scroll');
    }
}

function closeLeftSidebar() {
    const sidebar = document.getElementById('notes-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const btn = document.getElementById('left-menu-btn');
    
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    btn.classList.remove('active');
    document.body.classList.remove('no-scroll');
}

function closeRightSidebar() {
    const sidebar = document.getElementById('right-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const btn = document.getElementById('right-menu-btn');
    
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    btn.classList.remove('active');
    document.body.classList.remove('no-scroll');
}

function closeSidebars() {
    const leftSidebar = document.getElementById('notes-sidebar');
    const rightSidebar = document.getElementById('right-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const leftBtn = document.getElementById('left-menu-btn');
    const rightBtn = document.getElementById('right-menu-btn');
    
    if (leftSidebar) leftSidebar.classList.remove('open');
    if (rightSidebar) rightSidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
    if (leftBtn) leftBtn.classList.remove('active');
    if (rightBtn) rightBtn.classList.remove('active');
    
    document.body.classList.remove('no-scroll');
}

function initApp() {
    // Load folders
    loadFolders();

    // Load notes or bin
    if (document.getElementById('notes-list')) {
        loadNotes();
    }

    if (document.getElementById('bin-list')) {
        loadBin();
    }

    // Set up form handlers
    const noteForm = document.getElementById('note-form');
    if (noteForm) {
        noteForm.addEventListener('submit', handleCreateNote);
    }

    const folderForm = document.getElementById('folder-form');
    if (folderForm) {
        folderForm.addEventListener('submit', handleCreateFolder);
    }

    // Modal click outside to close
    const modal = document.getElementById('create-note-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideCreateNoteModal();
            }
        });
    }
    
    // Handle navigation items with data-href attribute
    document.addEventListener('click', (e) => {
        const item = e.target.closest('[data-href]');
        if (item) {
            const href = item.getAttribute('data-href');
            if (href) {
                window.location.href = href;
            }
        }
    });
    
    // Close sidebars on window resize if switching to desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            closeSidebars();
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

