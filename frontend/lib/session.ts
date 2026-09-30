const PROFILE_KEY = "finsarthi.profileId";
const RESULT_KEY = "finsarthi.resultId";

export function getStoredProfileId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(PROFILE_KEY);
}

export function setStoredProfileId(profileId: string): void {
  window.localStorage.setItem(PROFILE_KEY, profileId);
}

export function getStoredResultId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(RESULT_KEY);
}

export function setStoredResultId(resultId: string): void {
  window.localStorage.setItem(RESULT_KEY, resultId);
}

export function clearStoredResultId(): void {
  window.localStorage.removeItem(RESULT_KEY);
}
