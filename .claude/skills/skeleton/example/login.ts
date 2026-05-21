/*
 * login.ts — user authentication: sign in and sign out.
 *
 * Depends on:
 *   - bcrypt (password hashing)
 *   - ../db/users (users + sessions table access)
 *
 * Data shapes:
 *   User has: id (number), email (string), passwordHash (string), createdAt (date).
 *   LoginResult has: token (string) and expiresAt (date).
 */

import bcrypt from "bcrypt";
import { usersTable, sessionsTable } from "../db/users";
import { HttpError } from "../http/errors";

// Sign a user in: verify credentials, issue a session token.
async function login(email: string, password: string): Promise<LoginResult> {
  // - Look up the user by email in the users table.
  const user = await usersTable.findByEmail(email);

  // - If the user is missing, send back 404 "not found".
  if (!user) throw new HttpError(404, "not found");

  // - Compare the supplied password to the stored hash using bcrypt.
  const ok = await bcrypt.compare(password, user.passwordHash);

  // - If the comparison fails, send back 401 "invalid credentials".
  if (!ok) throw new HttpError(401, "invalid credentials");

  // - Create a new session token tied to the user id.
  const token = createToken(user.id);

  // - Store the token in the sessions table with a 24-hour expiry.
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);
  await sessionsTable.insert({ token, userId: user.id, expiresAt });

  // - Send back a LoginResult containing the token and its expiry.
  return { token, expiresAt };
}

// Sign a user out: drop the session. Idempotent.
async function logout(token: string): Promise<void> {
  // - Look up the session by token.
  const session = await sessionsTable.findByToken(token);

  // - If not found, stop (idempotent).
  if (!session) return;

  // - Otherwise, delete the session row.
  await sessionsTable.deleteByToken(token);
}
