/**
 * Form validation utilities for authentication forms
 */

export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Validate email format
 */
export function validateEmail(email: string): string | null {
  if (!email) {
    return "Email is required";
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return "Please enter a valid email address";
  }

  return null;
}

/**
 * Validate password strength
 */
export function validatePassword(password: string): string | null {
  if (!password) {
    return "Password is required";
  }

  if (password.length < 8) {
    return "Password must be at least 8 characters long";
  }

  // Optional: Add more strength requirements
  // const hasUpperCase = /[A-Z]/.test(password);
  // const hasLowerCase = /[a-z]/.test(password);
  // const hasNumber = /[0-9]/.test(password);
  // const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  //
  // if (!hasUpperCase || !hasLowerCase || !hasNumber) {
  //   return "Password must contain uppercase, lowercase, and numbers";
  // }

  return null;
}

/**
 * Validate password confirmation
 */
export function validatePasswordConfirmation(
  password: string,
  confirmation: string
): string | null {
  if (!confirmation) {
    return "Please confirm your password";
  }

  if (password !== confirmation) {
    return "Passwords do not match";
  }

  return null;
}

/**
 * Validate registration form
 */
export function validateRegistrationForm(data: {
  email: string;
  password: string;
  passwordConfirm?: string;
}): ValidationError[] {
  const errors: ValidationError[] = [];

  const emailError = validateEmail(data.email);
  if (emailError) {
    errors.push({ field: "email", message: emailError });
  }

  const passwordError = validatePassword(data.password);
  if (passwordError) {
    errors.push({ field: "password", message: passwordError });
  }

  if (data.passwordConfirm !== undefined) {
    const confirmError = validatePasswordConfirmation(
      data.password,
      data.passwordConfirm
    );
    if (confirmError) {
      errors.push({ field: "passwordConfirm", message: confirmError });
    }
  }

  return errors;
}

/**
 * Validate login form
 */
export function validateLoginForm(data: {
  email: string;
  password: string;
}): ValidationError[] {
  const errors: ValidationError[] = [];

  const emailError = validateEmail(data.email);
  if (emailError) {
    errors.push({ field: "email", message: emailError });
  }

  if (!data.password) {
    errors.push({ field: "password", message: "Password is required" });
  }

  return errors;
}

/**
 * Get error message for a specific field
 */
export function getFieldError(
  errors: ValidationError[],
  field: string
): string | null {
  const error = errors.find((e) => e.field === field);
  return error ? error.message : null;
}

/**
 * Validate brand name
 */
export function validateBrandName(brandName: string): string | null {
  if (!brandName || !brandName.trim()) {
    return "Brand name is required";
  }

  if (brandName.trim().length > 255) {
    return "Brand name must be 255 characters or less";
  }

  return null;
}

/**
 * Validate competitor name
 */
export function validateCompetitorName(competitorName: string): string | null {
  if (!competitorName || !competitorName.trim()) {
    return "Competitor name is required";
  }

  if (competitorName.trim().length > 255) {
    return "Competitor name must be 255 characters or less";
  }

  return null;
}

/**
 * Validate prompt text
 */
export function validatePromptText(promptText: string): string | null {
  if (!promptText || !promptText.trim()) {
    return "Prompt text is required";
  }

  if (promptText.trim().length > 1000) {
    return "Prompt text must be 1000 characters or less";
  }

  return null;
}
