document.addEventListener('alpine:init', () => {
    // --- 新增: Alpine.js 组件定义 ---
    // 这个组件负责管理文件树中每个节点的状态（比如是否展开）
    Alpine.data('fileTreeNode', (node) => ({
        node: node,
        open: node.open || false,
    }));

    // The main global store for the IDE (no changes here, just context)
    Alpine.store('ide', {
        // State properties
        projectList: null,
        selectedProject: null,
        fileTree: null,
        editor: null,
        currentFile: { path: null, content: null, originalContent: null },
        isDirty: false,
        projectToCreate: null,
        projectModal: null,

        // Initialization method
        init() {
            this.fetchProjectList();
            this.projectModal = new bootstrap.Modal(document.getElementById('setProjectModal'));
            window.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    if (this.isDirty) this.saveFile();
                }
            });

            // Watch for project selection to initialize the editor
            Alpine.effect(() => {
                if (this.selectedProject && !this.editor) {
                    setTimeout(() => this.initEditor(), 0);
                }
            });
        },
        
        // --- Methods (no changes from here down) ---

        fetchProjectList() {
            fetch('/api/projects/all')
                .then(res => res.json())
                .then(data => { this.projectList = data; })
                .catch(err => console.error('Failed to fetch project list:', err));
        },

        selectProject(projectId) {
            if (!projectId) return;
            const project = this.projectList.find(p => p.id == projectId);
            if (project) {
                this.selectedProject = project;
                this.fetchProjectFileTree(project.path);
            }
        },

        switchProject() {
            this.selectedProject = null;
            this.fileTree = null;
            this.currentFile = { path: null, content: null, originalContent: null };
            this.isDirty = false;
            if (this.editor) {
                this.editor.toTextArea(); // Properly revert CodeMirror to a textarea
                this.editor = null;
            }
        },

        fetchProjectFileTree(path) {
            this.fileTree = null; // Show loading state
            fetch(`/api/files/tree?path=${encodeURIComponent(path)}`)
                .then(res => res.json())
                .then(data => { this.fileTree = data; })
                .catch(err => console.error('Failed to fetch file tree:', err));
        },

        initEditor() {
            if (this.editor) return;
            const textarea = document.getElementById('editor-textarea');
            if (!textarea) return;
            
            this.editor = CodeMirror.fromTextArea(textarea, {
                lineNumbers: true,
                mode: 'python',
                theme: 'material-darker',
                lineWrapping: true,
                readOnly: true,
            });

            this.editor.setValue("// Select a file from the tree to begin editing.");
            
            this.editor.on('change', () => {
                this.isDirty = this.editor.getValue() !== this.currentFile.originalContent;
            });
        },

        openFile(path) {
            if (!this.editor) return;
            if (this.isDirty && !confirm('You have unsaved changes. Discard them?')) return;

            fetch(`/api/files/content?path=${encodeURIComponent(path)}`)
                .then(res => res.json())
                .then(data => {
                    this.currentFile = { path: data.path, content: data.content, originalContent: data.content };
                    this.isDirty = false;
                    this.editor.setValue(data.content);
                    this.editor.setOption('readOnly', false);
                    this.editor.focus();
                })
                .catch(err => alert(`Could not open file: ${path}. See console for details.`));
        },

        saveFile() {
            if (!this.currentFile.path || !this.isDirty) return;
            const newContent = this.editor.getValue();
            const saveBtn = document.querySelector('#editor-status button');
            const originalBtnHtml = saveBtn.innerHTML;
            saveBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Saving...`;
            saveBtn.disabled = true;

            fetch('/api/files/content', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: this.currentFile.path, content: newContent })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    this.currentFile.originalContent = newContent;
                    this.isDirty = false;
                } else {
                    alert('Error saving file: ' + data.detail);
                }
            })
            .catch(err => alert('A network error occurred while saving.'))
            .finally(() => {
                saveBtn.innerHTML = `<i class="bi bi-save me-1"></i> Save`;
                saveBtn.disabled = false;
            });
        },
        
        getRelativePath(fullPath) {
            if (!fullPath) return '';
            const PROJECTS_DIR_STR = window.ECHOPS_IDE_CONFIG.projectsDir;
            return fullPath.startsWith(PROJECTS_DIR_STR)
                ? '~' + fullPath.substring(PROJECTS_DIR_STR.length).replace(/\\/g, '/')
                : fullPath;
        },

        isTopLevelProject(path) {
            const PROJECTS_DIR_STR = window.ECHOPS_IDE_CONFIG.projectsDir;
            const parent = path.substring(0, path.lastIndexOf(path.includes('/') ? '/' : '\\'));
            return parent === PROJECTS_DIR_STR;
        },

        showProjectModal(node) {
            this.projectToCreate = node;
            const form = document.querySelector('#setProjectModal form');
            if (form) form.reset();
            const feedbackEl = document.getElementById('project-creation-feedback');
            if (feedbackEl) feedbackEl.innerHTML = '';
            this.projectModal.show();
        },

        getConfigCandidates(node) {
            if (!node || !node.children) return [];
            return node.children.filter(child => child.type === 'file' && (child.name.endsWith('.py') || child.name.endsWith('.json')));
        },

        createProject(event) {
            const formData = new FormData(event.target);
            formData.append('project_path', this.projectToCreate.path);
            const feedbackEl = document.getElementById('project-creation-feedback');
            feedbackEl.innerHTML = '';

            fetch('/api/projects/from-ide', { 
                method: 'POST', 
                body: formData 
            })
            .then(res => res.json().then(data => ({ ok: res.ok, data })))
            .then(({ ok, data }) => {
                if (!ok) {
                    throw new Error(data.detail || 'An unknown error occurred.');
                }
                feedbackEl.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                this.fetchProjectList();
                setTimeout(() => {
                    this.projectModal.hide();
                }, 1500);
            })
            .catch(err => {
                feedbackEl.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
            });
        }
    });
});