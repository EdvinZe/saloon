export interface Service {
  id: string
  name: string
  desc: string
  price: string
  priceNum: number
  dur: string
}

export interface Master {
  id: string
  name: string
  role: string
  initials: string
  tags: string[]
}

export const SERVICES: Service[] = [
  { id: 'haircut', name: 'Haircut', desc: 'Classic, fade, undercut — crafted to your face shape and lifestyle.', price: 'from €25', priceNum: 25, dur: '45 min' },
  { id: 'beard',   name: 'Beard',   desc: 'Shape, trim, sculpt. Hot towel and blade finish included.',           price: 'from €18', priceNum: 18, dur: '30 min' },
  { id: 'combo',   name: 'Combo',   desc: 'The full look. Haircut and beard in one visit. Most popular choice.', price: 'from €38', priceNum: 38, dur: '75 min' },
]

export const MOCK_MASTERS: Master[] = [
  { id: '1', name: 'Alex Kravtsov',  role: 'Senior barber',    initials: 'AK', tags: ['Classic', 'Fade', 'Beard'] },
  { id: '2', name: 'Michael Dorosh', role: 'Style specialist',  initials: 'MD', tags: ['Texture', 'Modern', 'Colour'] },
  { id: '3', name: 'Ivan Semenov',   role: 'Shave master',      initials: 'IS', tags: ['Royal shave', 'Hot towel'] },
  { id: '4', name: 'David Melnyk',   role: 'Colour expert',     initials: 'DM', tags: ['Highlights', 'Grey blend', 'Fade'] },
  { id: '5', name: 'Paul Kowalski',  role: 'Classic barber',    initials: 'PK', tags: ['Scissor cut', 'Pompadour'] },
]
