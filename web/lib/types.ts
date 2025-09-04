export type School = {
  id: string; // vestigings_id
  school_name: string;
  city: string | null;
  province: string | null;
  latitude: number | null;
  longitude: number | null;
  website: string | null;
  phone_formatted: string | null;
  has_website: boolean | null;
  education_structure: string | null;
  levels_offered: string | null;
  vmbo: boolean | null;
  havo: boolean | null;
  vwo: boolean | null;
  pro: boolean | null;
  mavo: boolean | null;
  brugjaar: boolean | null;
  enrollment_total: number | null;
  school_size_category: string | null;
  denomination: string | null;
  created_at: string | null;
};

