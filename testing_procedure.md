# Testing Procedure

This document describes the testing procedures used to verify the functionality, reliability, and correctness of the Campus Lost & Found Web Application. Testing includes both manual functional testing and basic automated tests.

---

## 1. Manual Testing

Manual testing was performed to validate user-facing features and ensure correct system behavior across common usage scenarios.

### 1.1 Post Lost or Found Item

**Steps:**
1. Navigate to the home page.
2. Click the “Post Item” button.
3. Fill out the form with a title, description, category, location, and contact information.
4. (Optional) Upload an image file (JPG, PNG, or GIF).
5. Submit the form.

**Expected Result:**
- The item is successfully saved to the database.
- The image is uploaded to the `static/uploads/` directory (if provided).
- A confirmation page is displayed showing the Item ID and deletion code.
- The posted item appears on the home page.

---

### 1.2 Browse Items

**Steps:**
1. Navigate to the home page.
2. View the list of posted items.

**Expected Result:**
- Items are displayed in a grid layout.
- Items appear in reverse chronological order (newest first).
- Each item displays its image, title, category, location, and date posted.

---

### 1.3 View Item Details

**Steps:**
1. Click the “View Details” button on any item.

**Expected Result:**
- The application navigates to the item detail page.
- Full item information is displayed, including description, contact information, and Item ID.
- If the item ID does not exist, a 404 error page is shown.

---

### 1.4 Mark Item as Found (Delete)

**Steps:**
1. Navigate to the “Mark as Found” or delete form.
2. Enter the Item ID.
3. Enter the deletion code provided when the item was posted.
4. Submit the form.

**Expected Result:**
- If the Item ID and deletion code match, the item is deleted from the database.
- The associated image file is removed from the uploads directory.
- A success message is displayed.
- If the deletion code is incorrect, an error message is shown and the item remains unchanged.

---

### 1.5 Image Upload Validation

**Steps:**
1. Attempt to upload an unsupported file type (e.g., `.txt` or `.exe`).
2. Attempt to upload an image larger than 16MB.

**Expected Result:**
- The system rejects unsupported file types.
- The system rejects files exceeding the maximum allowed size.
- An appropriate error message is displayed.

---


This testing procedure demonstrates that the application meets its functional requirements and behaves as expected under typical user interactions.
