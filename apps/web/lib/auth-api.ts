/**
 * Authentication API client methods
 *
 * Wraps the base API client with auth-specific methods
 */

import { apiClient, APIError } from "./api-client";

export interface RegisterData {
  email: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  verified: boolean;
  created_at: string;
}

export interface VerifyEmailData {
  token: string;
}

/**
 * Register a new user account
 */
export async function register(data: RegisterData): Promise<User> {
  try {
    return await apiClient.post<User>("/api/v1/auth/register", data);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError("Registration failed", 500);
  }
}

/**
 * Login with email and password
 */
export async function login(data: LoginData): Promise<User> {
  try {
    return await apiClient.post<User>("/api/v1/auth/login", data);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError("Login failed", 500);
  }
}

/**
 * Logout current user
 */
export async function logout(): Promise<void> {
  try {
    await apiClient.post("/api/v1/auth/logout");
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError("Logout failed", 500);
  }
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
  try {
    return await apiClient.get<User>("/api/v1/auth/me");
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError("Failed to get current user", 500);
  }
}

/**
 * Verify email address with token
 */
export async function verifyEmail(data: VerifyEmailData): Promise<User> {
  try {
    return await apiClient.post<User>("/api/v1/auth/verify", data);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError("Email verification failed", 500);
  }
}
