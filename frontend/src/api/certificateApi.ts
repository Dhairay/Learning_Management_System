import { apiRequest } from './httpClient';
import type { Certificate } from '../types';

export const certificateApi = {
  issueCertificate: (enrollmentId: string) =>
    apiRequest<Certificate>(`/enrollments/${enrollmentId}/certificate/issue/`, {
      method: 'POST',
    }),

  getCertificate: (certificateId: string) =>
    apiRequest<Certificate>(`/certificates/${certificateId}/`),

  verifyCertificate: (certificateNumber: string) =>
    apiRequest<{
      valid: boolean;
      certificate?: Certificate;
      message?: string;
    }>(`/certificates/verify/${certificateNumber}/`),
};
