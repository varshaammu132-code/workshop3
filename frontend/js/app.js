/**
 * EduTrack - Student Management System
 * Frontend Client Application
 * Handles API communication, UI rendering, modals, and notifications.
 */

// Determine API base URL (works seamlessly when served directly or via separate port)
const API_BASE_URL = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
  ? window.location.origin
  : "http://127.0.0.1:8000";

// State
let studentsList = [];
let editingStudentId = null;
let deletingStudentId = null;
let searchDebounceTimer = null;

// DOM Elements
const studentsTable = document.getElementById("studentsTable");
const studentsTableBody = document.getElementById("studentsTableBody");
const tableLoading = document.getElementById("tableLoading");
const emptyState = document.getElementById("emptyState");
const emptyStateMsg = document.getElementById("emptyStateMsg");
const resultsCount = document.getElementById("resultsCount");

// Search & Filter elements
const searchInput = document.getElementById("searchInput");
const clearSearchBtn = document.getElementById("clearSearchBtn");
const departmentFilter = document.getElementById("departmentFilter");
const semesterFilter = document.getElementById("semesterFilter");
const resetFiltersBtn = document.getElementById("resetFiltersBtn");
const refreshBtn = document.getElementById("refreshBtn");

// Stats elements
const totalStudentsCount = document.getElementById("totalStudentsCount");
const totalDeptsCount = document.getElementById("totalDeptsCount");
const backendStatusText = document.getElementById("backendStatusText");

// Modal elements (Add / Edit)
const studentModal = document.getElementById("studentModal");
const studentForm = document.getElementById("studentForm");
const modalTitle = document.getElementById("modalTitle");
const modalIcon = document.getElementById("modalIcon");
const saveBtnText = document.getElementById("saveBtnText");
const formAlert = document.getElementById("formAlert");
const studentIdInput = document.getElementById("studentId");
const studentUsnInput = document.getElementById("studentUsn");
const studentNameInput = document.getElementById("studentName");
const studentEmailInput = document.getElementById("studentEmail");
const studentPhoneInput = document.getElementById("studentPhone");
const studentDeptInput = document.getElementById("studentDept");
const studentSemesterInput = document.getElementById("studentSemester");
const openAddModalBtn = document.getElementById("openAddModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const cancelModalBtn = document.getElementById("cancelModalBtn");
const emptyStateActionBtn = document.getElementById("emptyStateActionBtn");

// Delete confirmation modal elements
const deleteModal = document.getElementById("deleteModal");
const deleteStudentName = document.getElementById("deleteStudentName");
const deleteStudentUsn = document.getElementById("deleteStudentUsn");
const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");
const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

// Toast Container
const toastContainer = document.getElementById("toastContainer");

// ====================================================================
// INITIALIZATION
// ====================================================================
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  loadStudentsAndStats();
});

function initEventListeners() {
  // Modal open & close
  openAddModalBtn.addEventListener("click", () => openStudentModal());
  emptyStateActionBtn.addEventListener("click", () => openStudentModal());
  closeModalBtn.addEventListener("click", closeStudentModal);
  cancelModalBtn.addEventListener("click", closeStudentModal);

  // Close modals on clicking outside
  studentModal.addEventListener("click", (e) => {
    if (e.target === studentModal) closeStudentModal();
  });
  deleteModal.addEventListener("click", (e) => {
    if (e.target === deleteModal) closeDeleteModal();
  });

  // Form submit
  studentForm.addEventListener("submit", handleFormSubmit);

  // Delete modal actions
  cancelDeleteBtn.addEventListener("click", closeDeleteModal);
  confirmDeleteBtn.addEventListener("click", handleConfirmDelete);

  // Search input with debounce
  searchInput.addEventListener("input", (e) => {
    const value = e.target.value.trim();
    clearSearchBtn.style.display = value ? "block" : "none";
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      fetchStudents();
    }, 280);
  });

  clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearSearchBtn.style.display = "none";
    fetchStudents();
  });

  // Filter change events
  departmentFilter.addEventListener("change", () => fetchStudents());
  semesterFilter.addEventListener("change", () => fetchStudents());

  // Reset filters
  resetFiltersBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearSearchBtn.style.display = "none";
    departmentFilter.value = "All";
    semesterFilter.value = "All";
    fetchStudents();
  });

  // Refresh button
  refreshBtn.addEventListener("click", () => {
    showToast("Refreshing student data...", "info");
    loadStudentsAndStats();
  });

  // Auto capitalize USN input
  studentUsnInput.addEventListener("input", (e) => {
    e.target.value = e.target.value.toUpperCase();
  });
}

// ====================================================================
// API FUNCTIONS
// ====================================================================

async function loadStudentsAndStats() {
  await Promise.all([fetchStudents(), fetchStats()]);
}

/**
 * Fetch students from the backend with current search & filter parameters.
 */
async function fetchStudents() {
  showLoading(true);

  const search = searchInput.value.trim();
  const dept = departmentFilter.value;
  const sem = semesterFilter.value;

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (dept && dept !== "All") params.append("department", dept);
  if (sem && sem !== "All") params.append("semester", sem);

  const queryString = params.toString() ? `?${params.toString()}` : "";

  try {
    const response = await fetch(`${API_BASE_URL}/api/students${queryString}`);
    if (!response.ok) {
      throw new Error(`Failed to load students (Status: ${response.status})`);
    }

    studentsList = await response.json();
    backendStatusText.textContent = "Connected";
    renderStudentsTable(studentsList);
    updateResultsInfo(studentsList.length);
  } catch (error) {
    console.error("Error fetching students:", error);
    backendStatusText.textContent = "Offline";
    showToast("Could not connect to backend server. Make sure FastAPI is running.", "error");
    renderEmptyState("Unable to reach backend server. Please verify the Python server is running.");
  } finally {
    showLoading(false);
  }
}

/**
 * Fetch statistical summary for the dashboard cards.
 */
async function fetchStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    if (response.ok) {
      const stats = await response.json();
      totalStudentsCount.textContent = stats.total_students;
      totalDeptsCount.textContent = stats.departments_count;
    }
  } catch (err) {
    console.warn("Could not fetch stats:", err);
  }
}

/**
 * Handle Add/Update form submission.
 */
async function handleFormSubmit(e) {
  e.preventDefault();
  hideFormAlert();

  // Extract form inputs
  const usn = studentUsnInput.value.trim().toUpperCase();
  const name = studentNameInput.value.trim();
  const email = studentEmailInput.value.trim();
  const phone = studentPhoneInput.value.trim();
  const department = studentDeptInput.value;
  const semester = parseInt(studentSemesterInput.value, 10);
  const genderRadio = document.querySelector('input[name="studentGender"]:checked');
  const gender = genderRadio ? genderRadio.value : "Other";

  // Client Validation
  if (!usn || !name || !email || !phone || !department || !semester) {
    showFormAlert("Please fill in all required fields.");
    return;
  }

  if (name.length < 2) {
    showFormAlert("Name must be at least 2 characters long.");
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showFormAlert("Please enter a valid email address.");
    return;
  }

  const payload = {
    usn,
    name,
    email,
    phone,
    department,
    semester,
    gender
  };

  const isEditing = editingStudentId !== null;
  const url = isEditing
    ? `${API_BASE_URL}/api/students/${editingStudentId}`
    : `${API_BASE_URL}/api/students`;
  const method = isEditing ? "PUT" : "POST";

  setSaveBtnLoading(true);

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (!res.ok) {
      const errorMessage = data.detail || "Failed to save student details.";
      showFormAlert(errorMessage);
      return;
    }

    // Success!
    closeStudentModal();
    showToast(
      isEditing
        ? `Student '${name}' updated successfully!`
        : `Student '${name}' registered successfully!`,
      "success"
    );

    // Refresh table and stats
    await loadStudentsAndStats();

  } catch (error) {
    console.error("Submission error:", error);
    showFormAlert("An error occurred while connecting to the server. Please try again.");
  } finally {
    setSaveBtnLoading(false);
  }
}

/**
 * Confirm and delete student record.
 */
async function handleConfirmDelete() {
  if (!deletingStudentId) return;

  confirmDeleteBtn.disabled = true;
  confirmDeleteBtn.textContent = "Deleting...";

  try {
    const res = await fetch(`${API_BASE_URL}/api/students/${deletingStudentId}`, {
      method: "DELETE"
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Could not delete student.");
    }

    closeDeleteModal();
    showToast("Student record deleted successfully.", "success");
    await loadStudentsAndStats();

  } catch (error) {
    console.error("Delete error:", error);
    showToast(error.message || "Failed to delete student.", "error");
  } finally {
    confirmDeleteBtn.disabled = false;
    confirmDeleteBtn.textContent = "Yes, Delete Record";
  }
}

// ====================================================================
// UI RENDERING & HELPERS
// ====================================================================

function renderStudentsTable(students) {
  studentsTableBody.innerHTML = "";

  if (!students || students.length === 0) {
    renderEmptyState();
    return;
  }

  studentsTable.style.display = "table";
  emptyState.style.display = "none";

  students.forEach((student, index) => {
    const tr = document.createElement("tr");

    // Initials & avatar color
    const initials = getInitials(student.name);
    const avatarColor = getAvatarColor(student.name);
    const deptClass = getDeptClass(student.department);

    tr.innerHTML = `
      <td><span style="color: #94a3b8; font-weight: 600;">${index + 1}</span></td>
      <td>
        <div class="student-profile">
          <div class="avatar" style="background: ${avatarColor};">${initials}</div>
          <div class="student-meta">
            <span class="student-name">${escapeHtml(student.name)}</span>
            <span class="student-email">${escapeHtml(student.email)}</span>
          </div>
        </div>
      </td>
      <td><span class="usn-badge">${escapeHtml(student.usn)}</span></td>
      <td><span class="dept-badge ${deptClass}">${escapeHtml(student.department)}</span></td>
      <td><span class="sem-badge">Sem ${student.semester}</span></td>
      <td style="color: #334155; font-size: 0.85rem;">${escapeHtml(student.phone)}</td>
      <td>
        <span class="gender-tag">
          ${student.gender === "Male" ? "👨 Male" : student.gender === "Female" ? "👩 Female" : "🧑 Other"}
        </span>
      </td>
      <td class="text-right">
        <div class="action-buttons">
          <button class="action-btn action-btn-edit" title="Edit Student" onclick="openEditModal(${student.id})">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
          </button>
          <button class="action-btn action-btn-delete" title="Delete Student" onclick="openDeleteConfirm(${student.id})">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
          </button>
        </div>
      </td>
    `;

    studentsTableBody.appendChild(tr);
  });
}

function renderEmptyState(customMsg) {
  studentsTable.style.display = "none";
  emptyState.style.display = "flex";
  if (customMsg) {
    emptyStateMsg.textContent = customMsg;
  } else {
    const isSearching = searchInput.value.trim() || departmentFilter.value !== "All" || semesterFilter.value !== "All";
    emptyStateMsg.textContent = isSearching
      ? "No students match your search filter criteria. Try clearing filters."
      : "No students registered yet. Click 'Add New Student' to get started!";
  }
}

function updateResultsInfo(count) {
  const isFiltered = searchInput.value.trim() || departmentFilter.value !== "All" || semesterFilter.value !== "All";
  if (isFiltered) {
    resultsCount.textContent = `Found ${count} student${count === 1 ? "" : "s"} matching filters`;
  } else {
    resultsCount.textContent = `Showing all ${count} student${count === 1 ? "" : "s"}`;
  }
}

function showLoading(show) {
  if (show) {
    tableLoading.style.display = "flex";
    studentsTable.style.display = "none";
    emptyState.style.display = "none";
  } else {
    tableLoading.style.display = "none";
  }
}

// ====================================================================
// MODAL CONTROLLERS
// ====================================================================

function openStudentModal(isEdit = false) {
  editingStudentId = isEdit ? editingStudentId : null;
  hideFormAlert();

  if (isEdit) {
    modalTitle.textContent = "Edit Student Details";
    modalIcon.textContent = "✏️";
    saveBtnText.textContent = "Update Student Details";
  } else {
    studentForm.reset();
    studentIdInput.value = "";
    document.querySelector('input[name="studentGender"][value="Male"]').checked = true;
    modalTitle.textContent = "Register New Student";
    modalIcon.textContent = "🎓";
    saveBtnText.textContent = "Save Student";
  }

  studentModal.style.display = "flex";
  studentUsnInput.focus();
}

function closeStudentModal() {
  studentModal.style.display = "none";
  hideFormAlert();
  editingStudentId = null;
}

window.openEditModal = function(id) {
  const student = studentsList.find(s => s.id === id);
  if (!student) {
    showToast("Student record not found.", "error");
    return;
  }

  editingStudentId = id;
  studentIdInput.value = student.id;
  studentUsnInput.value = student.usn;
  studentNameInput.value = student.name;
  studentEmailInput.value = student.email;
  studentPhoneInput.value = student.phone;
  studentDeptInput.value = student.department;
  studentSemesterInput.value = student.semester;

  const genderRadio = document.querySelector(`input[name="studentGender"][value="${student.gender}"]`);
  if (genderRadio) {
    genderRadio.checked = true;
  }

  openStudentModal(true);
};

window.openDeleteConfirm = function(id) {
  const student = studentsList.find(s => s.id === id);
  if (!student) return;

  deletingStudentId = id;
  deleteStudentName.textContent = student.name;
  deleteStudentUsn.textContent = student.usn;
  deleteModal.style.display = "flex";
};

function closeDeleteModal() {
  deleteModal.style.display = "none";
  deletingStudentId = null;
}

function showFormAlert(message) {
  formAlert.textContent = message;
  formAlert.style.display = "block";
}

function hideFormAlert() {
  formAlert.textContent = "";
  formAlert.style.display = "none";
}

function setSaveBtnLoading(loading) {
  const btn = document.getElementById("saveStudentBtn");
  if (loading) {
    btn.disabled = true;
    saveBtnText.textContent = "Saving...";
  } else {
    btn.disabled = false;
    saveBtnText.textContent = editingStudentId ? "Update Student Details" : "Save Student";
  }
}

// ====================================================================
// TOAST NOTIFICATIONS
// ====================================================================

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const icon = type === "success" ? "✓" : type === "error" ? "✕" : "ℹ";
  toast.innerHTML = `<span style="font-weight: 800; font-size: 1.1rem;">${icon}</span> <span>${escapeHtml(message)}</span>`;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, 3500);
}

// ====================================================================
// UTILITY FUNCTIONS
// ====================================================================

function getInitials(name) {
  if (!name) return "ST";
  const parts = name.trim().split(" ");
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return parts[0].slice(0, 2).toUpperCase();
}

function getAvatarColor(str) {
  const colors = [
    "linear-gradient(135deg, #6366f1, #4f46e5)",
    "linear-gradient(135deg, #0ea5e9, #0284c7)",
    "linear-gradient(135deg, #10b981, #059669)",
    "linear-gradient(135deg, #8b5cf6, #7c3aed)",
    "linear-gradient(135deg, #f59e0b, #d97706)",
    "linear-gradient(135deg, #ec4899, #db2777)"
  ];
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % colors.length;
  return colors[index];
}

function getDeptClass(dept) {
  if (!dept) return "dept-def";
  const d = dept.toLowerCase();
  if (d.includes("computer")) return "dept-cs";
  if (d.includes("information")) return "dept-is";
  if (d.includes("electronic")) return "dept-ec";
  if (d.includes("machine") || d.includes("ai")) return "dept-ai";
  if (d.includes("mechanical")) return "dept-me";
  if (d.includes("civil")) return "dept-cv";
  return "dept-def";
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
