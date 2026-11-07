import { apiRequest } from './httpClient';
import type { User, Organization, OrganizationMembership } from '../types';

export const authApi = {
  login: (data: { email: string; password: string }) =>
    apiRequest<{ access: string; refresh: string }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  register: (data: { 
    email: string; 
    password: string; 
    first_name?: string; 
    last_name?: string; 
    role?: 'STUDENT' | 'INSTRUCTOR' | 'ORG_ADMIN';
    organization_name?: string; 
    organization_slug?: string;
  }) =>
    apiRequest<{ user: User; tokens: { access: string; refresh: string } }>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),


  getProfile: () =>
    apiRequest<{ user: User; memberships: OrganizationMembership[] }>('/me/'),

  updateProfile: (data: Partial<User>) =>
    apiRequest<User>('/me/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  getOrganizations: () =>
    apiRequest<Organization[]>('/organizations/'),

  createOrganization: (data: { name: string; description?: string }) =>
    apiRequest<Organization>('/organizations/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getOrgMembers: (orgSlug: string) =>
    apiRequest<OrganizationMembership[]>(`/organizations/${orgSlug}/members/`),

  inviteMember: (orgSlug: string, data: { email: string; role: string }) =>
    apiRequest(`/organizations/${orgSlug}/invitations/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateMemberRole: (orgSlug: string, membershipId: string, role: string) =>
    apiRequest(`/organizations/${orgSlug}/members/${membershipId}/roles/`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    }),

  acceptInvitation: (token: string) =>
    apiRequest('/auth/invitations/accept/', {
      method: 'POST',
      body: JSON.stringify({ token }),
    }),

  getRoles: () =>
    apiRequest<Array<{ id: string; name: string; display_name: string; description: string }>>('/auth/roles/'),

  provisionAdminUser: (data: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    role: 'SUPER_ADMIN' | 'ADMIN';
    institute_name?: string;
    institute_slug?: string;
    description?: string;
  }) =>
    apiRequest<{
      detail: string;
      user: User;
      organization?: Organization;
      memberships: OrganizationMembership[];
      tokens: { access: string; refresh: string };
    }>('/auth/admin-users/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getUsersDirectory: (roleFilter?: string) => {
    const query = roleFilter ? `?role=${encodeURIComponent(roleFilter)}` : '';
    return apiRequest<User[]>(`/auth/users/${query}`);
  },
};
