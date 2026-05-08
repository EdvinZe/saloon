export interface Service {
  id: string
  name: string
  desc: string
  price: string
  priceNum: number
  dur: string
  durationMin: number
  bufferMin: number
  isActive: boolean
}

export interface Master {
  id: string
  name: string
  role: string
  initials: string
  tags: string[]
  bio: string
  isActive: boolean
}

export const SERVICES: Service[] = [
  { id: 'haircut', name: 'Haircut', isActive: true, desc: 'Classic, fade, undercut — crafted to your face shape and lifestyle.', price: 'from €25', priceNum: 25, dur: '45 min', durationMin: 45, bufferMin: 15 },
  { id: 'beard',   name: 'Beard', isActive: true,  desc: 'Shape, trim, sculpt. Hot towel and blade finish included.',           price: 'from €18', priceNum: 18, dur: '30 min', durationMin: 30, bufferMin: 15 },
  { id: 'combo',   name: 'Combo', isActive: true,  desc: 'The full look. Haircut and beard in one visit. Most popular choice.', price: 'from €38', priceNum: 38, dur: '75 min', durationMin: 75, bufferMin: 15 },
]

export const MOCK_MASTERS: Master[] = [
  { id: '1', name: 'Alex Kravtsov',  role: 'Senior barber', isActive: true ,  initials: 'AK', tags: ['Classic', 'Fade', 'Beard'],             bio: 'Over 12 years behind the chair. Alex built his craft in St. Petersburg before bringing his precision to Vilnius. Every cut starts with a conversation.' },
  { id: '2', name: 'Michael Dorosh', role: 'Style specialist', isActive: true  , initials: 'MD', tags: ['Texture', 'Modern', 'Colour'],          bio: 'Michael studied at the Wahl Academy in Berlin and spent years in boutique studios across Europe. He reads a face the way others read a map.' },
  { id: '3', name: 'Ivan Semenov',   role: 'Shave master',   isActive: true ,   initials: 'IS', tags: ['Royal shave', 'Hot towel'],             bio: 'A straight-razor specialist with a reverence for ritual. Ivan\'s hot-towel shave is the slowest thing we offer — and the most requested.' },
  { id: '4', name: 'David Melnyk',   role: 'Colour expert',  isActive: true  ,   initials: 'DM', tags: ['Highlights', 'Grey blend', 'Fade'],     bio: 'David treats colour as a craft, not a formula. From seamless grey blends to bold contrasts, he works in light and shadow.' },
  { id: '5', name: 'Paul Kowalski',  role: 'Classic barber',  isActive: true  ,  initials: 'PK', tags: ['Scissor cut', 'Pompadour'],             bio: 'Paul grew up in his grandfather\'s Warsaw barbershop. Scissors only. He believes the best cut should look like it happened naturally.' },
]

export type AspectRatio = '1:1' | '3:4'

export interface WorkPhoto {
  id: string
  photo_url: string
  aspect_ratio: AspectRatio
  master_id: string
}

export const MOCK_WORKS: WorkPhoto[] = [
  { id: '1',  photo_url: '', aspect_ratio: '1:1', master_id: '1' },
  { id: '2',  photo_url: '', aspect_ratio: '3:4', master_id: '2' },
  { id: '3',  photo_url: '', aspect_ratio: '3:4', master_id: '3' },
  { id: '4',  photo_url: '', aspect_ratio: '1:1', master_id: '4' },
  { id: '5',  photo_url: '', aspect_ratio: '3:4', master_id: '5' },
  { id: '6',  photo_url: '', aspect_ratio: '3:4', master_id: '1' },
  { id: '7',  photo_url: '', aspect_ratio: '1:1', master_id: '2' },
  { id: '8',  photo_url: '', aspect_ratio: '3:4', master_id: '3' },
  { id: '9',  photo_url: '', aspect_ratio: '1:1', master_id: '4' },
  { id: '10', photo_url: '', aspect_ratio: '3:4', master_id: '5' },
  { id: '11', photo_url: '', aspect_ratio: '1:1', master_id: '1' },
  { id: '12', photo_url: '', aspect_ratio: '3:4', master_id: '2' },
  { id: '13', photo_url: '', aspect_ratio: '3:4', master_id: '3' },
  { id: '14', photo_url: '', aspect_ratio: '1:1', master_id: '4' },
  { id: '15', photo_url: '', aspect_ratio: '3:4', master_id: '5' },
  { id: '16', photo_url: '', aspect_ratio: '1:1', master_id: '1' },
  { id: '17', photo_url: '', aspect_ratio: '3:4', master_id: '2' },
  { id: '18', photo_url: '', aspect_ratio: '1:1', master_id: '3' },
  { id: '19', photo_url: '', aspect_ratio: '3:4', master_id: '4' },
  { id: '20', photo_url: '', aspect_ratio: '1:1', master_id: '5' },
  { id: '21', photo_url: '', aspect_ratio: '3:4', master_id: '1' },
  { id: '22', photo_url: '', aspect_ratio: '3:4', master_id: '2' },
  { id: '23', photo_url: '', aspect_ratio: '1:1', master_id: '3' },
  { id: '24', photo_url: '', aspect_ratio: '3:4', master_id: '4' },
  { id: '25', photo_url: '', aspect_ratio: '1:1', master_id: '5' },
  { id: '26', photo_url: '', aspect_ratio: '3:4', master_id: '1' },
  { id: '27', photo_url: '', aspect_ratio: '1:1', master_id: '2' },
]


export type ContactType = 'address' | 'phone' | 'instagram' | 'hours'

export interface ContactItem {
  type: ContactType
  label: string
  value: string
  url?: string
  isActive: boolean
}

export const CONTACT_ITEMS: ContactItem[] = [
  {
    type: 'address',
    label: 'Address',
    value: 'Gedimino pr. 14\nVilnius LT-01103',
    url: 'https://maps.google.com/?q=Gedimino+pr.+14+Vilnius',
    isActive: true,
  },
  {
    type: 'phone',
    label: 'Phone',
    value: '+370 600 00000',
    url: 'tel:+37060000000',
    isActive: true,
  },
  {
    type: 'instagram',
    label: 'Instagram',
    value: '@saloon.vilnius',
    url: 'https://instagram.com/saloon.vilnius',
    isActive: true,
  },
  {
    type: 'hours',
    label: 'Hours',
    value: 'Mon–Fri 10:00–20:00\nSat 10:00–18:00\nSun Closed',
    isActive: true,
  },
]