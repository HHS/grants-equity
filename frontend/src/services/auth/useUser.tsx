"use client";

import { UserContextType } from "src/services/auth/types";

import { createContext, useContext } from "react";

export const UserContext = createContext({} as UserContextType);

/**
 * @ignore
 */
export type UserContextHook = () => UserContextType;

/**
 * The `useUser` hook, which will get you the {@link UserProfile} object from the server-side session by fetching it
 * from the {@link HandleProfile} API route.
 *
 * ```js
 * import Link from 'next/link';
 * import { useUser } from 'src/services/auth/useUser';
 *
 * export default function Profile() {
 *   const { user, error, isLoading } = useUser();
 *
 *   if (isLoading) return <div>Loading...</div>;
 *   if (error) return <div>{error.message}</div>;
 *   if (!user) return <Link href="/api/auth/login"><a>Login</a></Link>;
 *   return <div>Hello {user.name}, <Link href="/api/auth/logout"><a>Logout</a></Link></div>;
 * }
 * ```
 *
 * @category Client
 */
export const useUser: UserContextHook = () =>
  useContext<UserContextType>(UserContext);
