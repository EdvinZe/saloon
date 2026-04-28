export interface Service {
  id: string
  name: string
  desc: string
  price: string
  priceNum: number
  dur: string
  durationMin: number
  bufferMin: number
}

export interface Master {
  id: string
  name: string
  role: string
  initials: string
  tags: string[]
}

export const SERVICES: Service[] = [
  { id: 'haircut', name: 'Haircut', desc: 'Classic, fade, undercut — crafted to your face shape and lifestyle.', price: 'from €25', priceNum: 25, dur: '45 min', durationMin: 45, bufferMin: 15 },
  { id: 'beard',   name: 'Beard',   desc: 'Shape, trim, sculpt. Hot towel and blade finish included.',           price: 'from €18', priceNum: 18, dur: '30 min', durationMin: 30, bufferMin: 15 },
  { id: 'combo',   name: 'Combo',   desc: 'The full look. Haircut and beard in one visit. Most popular choice.', price: 'from €38', priceNum: 38, dur: '75 min', durationMin: 75, bufferMin: 15 },
]

export const MOCK_MASTERS: Master[] = [
  { id: '1', name: 'Alex Kravtsov',  role: 'Senior barber',    initials: 'AK', tags: ['Classic', 'Fade', 'Beard'] },
  { id: '2', name: 'Michael Dorosh', role: 'Style specialist',  initials: 'MD', tags: ['Texture', 'Modern', 'Colour'] },
  { id: '3', name: 'Ivan Semenov',   role: 'Shave master',      initials: 'IS', tags: ['Royal shave', 'Hot towel'] },
  { id: '4', name: 'David Melnyk',   role: 'Colour expert',     initials: 'DM', tags: ['Highlights', 'Grey blend', 'Fade'] },
  { id: '5', name: 'Paul Kowalski',  role: 'Classic barber',    initials: 'PK', tags: ['Scissor cut', 'Pompadour'] },
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
