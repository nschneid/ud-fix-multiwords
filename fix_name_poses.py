"""
Used to fix PROPN tags that should be ADJ, ADV, or VERB.

Nathan Schneider (2021-05-01)
"""

import os
import sys
import io

from collections import defaultdict, Counter

from depgraph_utils import *

manual_review = []

c = defaultdict(Counter)   # lemma type => {'ADJ': __, 'NOUN': __}

# lemmas that show up in EWT more often as ADJ than NOUN
ADJS = ['1/2', 'anti-india', 'pro-india', 'shia', 'Sinhala', 'bella', 'extra', 'fab', 'pre-fab', 'Arab', 'non-Arab', 'dumb', 'superb', 'cardiac', 'sporadic', 'encyclopedic', 'specific', 'terrific', 'horrific', 'scientific', 'tragic', 'strategic', 'psychic', 'telegraphic', 'orthographic', 'demographic', 'catastrophic', 'public', 'symbolic', 'hyperbolic', 'acrylic', 'Islamic', 'ceramic', 'academic', 'anemic', 'comic', 'economic', 'cosmic', 'Satanic', 'schizophrenic', 'ethnic', 'iconic', 'hegemonic', 'chronic', 'ironic', 'electronic', 'Masonic', 'supersonic', 'neoplatonic', 'epic', 'microscopic', 'generic', 'historic', 'electric', 'metric', 'asymmetric', 'geometric', 'concentric', 'gastric', 'basic', 'intrinsic', 'dramatic', 'melodramatic', 'diplomatic', 'symptomatic', 'automatic', 'semi-automatic', 'semiautomatic', 'fanatic', 'theocratic', 'Democratic', 'democratic', 'anti-democratic', 'bureaucratic', 'erratic', 'electrostatic', 'hectic', 'arctic', 'apologetic', 'unapologetic', 'energetic', 'apathetic', 'sympathetic', 'synthetic', 'cosmetic', 'genetic', 'magnetic', 'transatlantic', 'romantic', 'authentic', 'exotic', 'quixotic', 'apocalyptic', 'aortic', 'stochastic', 'enthusiastic', 'plastic', 'fantastic', 'majestic', 'domestic', 'sadistic', 'realistic', 'unrealistic', 'journalistic', 'ballistic', 'holistic', 'optimistic', 'communistic', 'artistic', 'linguistic', 'therapeutic', 'catalytic', 'civic', 'toxic', 'defunctc', '3d', 'bad', 'dead', 'widespread', 'glad', 'mad', 'broad', 'sad', 'odd', 'faced', 'priced', 'over-priced', 'unpriced', 'overpriced', 'advanced', 'experienced', 'inexperienced', 'convinced', 'divorced', 'padded', 'unheeded', 'undecided', 'sided', 'lopsided', 'ended', 'offended', 'recommended', 'extended', 'minded', 'wounded', 'blooded', 'bearded', 'retarded', 'secluded', 'crowded', 'overcrowded', 'guaranteed', 'fed', 'proofed', 'aged', 'discouraged', 'advantaged', 'fledged', 'privileged', 'alleged', 'unchanged', 'attached', 'untouched', 'smashed', 'finished', 'astonished', 'distinguished', 'unspecified', 'qualified', 'terrified', 'classified', 'certified', 'justified', 'mystified', 'satisfied', 'dissatisfied', 'occupied', 'varied', 'dried', 'married', 'worried', 'naked', 'soaked', 'packed', 'picked', 'cocked', 'shocked', 'landlocked', 'overcooked', 'disabled', 'troubled', 'riddled', 'unparalleled', 'detailed', 'veiled', 'coiled', 'spoiled', 'appalled', 'pre-killed', 'skilled', 'thrilled', 'crippled', 'coupled', 'disgruntled', 'settled', 'ashamed', 'unnamed', 'armed', 'unconfirmed', 'informed', 'unscreened', 'enlightened', 'trained', 'untrained', 'unrestrained', 'entertained', 'inclined', 'redlined', 'determined', 'intertwined', 'manned', 'unmanned', 'skinned', 'fashioned', 'reasoned', 'seasoned', 'concerned', 'unturned', 'pre-owned', 'renowned', 'browned', 'shaped', 'cramped', 'handicapped', 'trapped', 'unequipped', 'zipped', 'red', 'scared', 'disappeared', 'undeclared', 'prepared', 'sacred', 'endangered', 'feathered', 'mannered', 'flustered', 'shattered', 'flattered', 'covered', 'inspired', 'uninspired', 'expired', 'tired', 'retired', 'bored', 'unexplored', 'armored', 'uncensored', 'flavored', 'preferred', 'blurred', 'injured', 'coloured', 'uninsured', 'pressured', 'based', 'pleased', 'biased', 'embarrased', 'dispossesed', 'unexercised', 'organised', 'apprised', 'surprised', 'licensed', 'closed', 'opposed', 'exposed', 'embarrassed', 'unprocessed', 'blessed', 'depressed', 'repressed', 'impressed', 'obsessed', 'used', 'focused', 'confused', 'amused', 'dedicated', 'complicated', 'pre-fabricated', 'sophisticated', 'educated', 'dated', 'updated', 'outdated', 'treated', 'untreated', 'fated', 'gated', 'obligated', 'associated', 'related', 'unrelated', 'isolated', 'coagulated', 'regulated', 'animated', 'automated', 'uncontaminated', 'over-rated', 'dehydrated', 'integrated', 'frustrated', 'affected', 'unaffected', 'infected', 'unconnected', 'respected', 'unexpected', 'unrestricted', 'delighted', 'unsolicited', 'excited', 'limited', 'unlimited', 'united', 'stilted', 'slanted', 'unwanted', 'accented', 'unprecedented', 'oriented', 'talented', 'untalented', 'acquainted', 'pointed', 'disappointed', 'vaunted', 'discounted', 'devoted', 'uninterrupted', 'concerted', 'converted', 'perverted', 'ported', 'wasted', 'unmolested', 'interested', 'vested', 'desisted', 'twisted', 'posted', 'fitted', 'committed', 'uncommitted', 'undisputed', 'bereaved', 'relieved', 'unresolved', 'involved', 'beloved', 'non-approved', 'slowed', 'newlywed', 'relaxed', 'fixed', 'mixed', 'delayed', 'betrayed', 'dyed', 'unemployed', 'annoyed', 'amazed', 'specialized', 'fertilized', 'unfertilized', 'civilized', 'organized', 'unorganized', 'unweaponized', 'sized', 'undersized', 'laid', 'unpaid', 'afraid', 'rabid', 'placid', 'splendid', 'valid', 'solid', 'timid', 'humid', 'paranoid', 'devoid', 'rapid', 'intrepid', 'bicuspid', 'stupid', 'rid', 'avid', 'vivid', 'bald', 'mild', 'wild', 'old', 'bold', 'cold', '2nd', 'bland', 'overland', 'grand', 'pretend', 'hind', 'blind', 'second', 'fond', 'bound', 'profound', 'newfound', 'underground', 'yound', 'good', 'unheard', 'hard', 'forward', 'straightforward', 'outward', 'weird', 'third', 'absurd', 'gud', 'loud', 'proud', 'shrewd', 'nice', 'freelance', 'scarce', 'spruce', 'renegade', 'homemade', 'streamside', 'outside', 'wide', 'worldwide', 'statewide', 'blonde', 'rude', 'free', 'wee', 'safe', 'unsafe', 'rife', 'teenage', 'underage', 'average', 'orange', 'strange', 'large', 'huge', 'loathe', 'ie', 'indie', 'eerie', 'fake', 'awake', 'like', 'alike', 'broke', 'upscale', 'wholesale', 'stale', 'able', 'probable', 'impeccable', 'applicable', 'formidable', 'unavoidable', 'understandable', 'dependable', 'refundable', 'affordable', 'laudable', 'traceable', 'noticeable', 'rideable', 'agreeable', 'knowledgeable', 'unknowledgeable', 'changeable', 'reachable', 'unreachable', 'approachable', 'untouchable', 'perishable', 'sociable', 'unsociable', 'reliable', 'unreliable', 'undeniable', 'insatiable', 'viable', 'unmistakable', 'unthinkable', 'workable', 'inhalable', 'available', 'irreconcilable', 'inalienable', 'trainable', 'actionable', 'reasonable', 'personable', 'unable', 'capable', 'unbearable', 'inseparable', 'comparable', 'considerable', 'preferable', 'transferable', 'tolerable', 'vulnerable', 'inoperable', 'miserable', 'desirable', 'undesirable', 'adorable', 'memorable', 'honorable', 'favorable', 'impenetrable', 'favourable', 'unfavourable', 'indispensable', 'reimbursable', 'passable', 'unbeatable', 'repeatable', 'unpalatable', 'intractable', 'contactable', 'delectable', 'respectable', 'detectable', 'predictable', 'unpredictable', 'profitable', 'hospitable', 'charitable', 'veritable', 'suitable', 'inevitable', 'notable', 'potable', 'acceptable', 'unacceptable', 'comfortable', 'uncomfortable', 'portable', 'unstable', 'adjustable', 'regrettable', 'attributable', 'executable', 'reputable', 'valuable', 'unbelievable', 'conceivable', 'unforgivable', 'lovable', 'renewable', 'fixable', 'payable', 'enjoyable', 'employable', 'unemployable', 'feeble', 'edible', 'credible', 'incredible', 'audible', 'eligible', 'tangible', 'gullible', 'terrible', 'horrible', 'feasible', 'visible', 'sensible', 'ostensible', 'responsible', 'accessible', 'possible', 'impossible', 'compatible', 'flexible', 'humble', 'noble', 'double', 'idle', 'single', 'mobile', 'fragile', 'worthwhile', 'sterile', 'virile', 'fertile', 'infertile', 'hostile', 'ramshackle', 'ole', 'whole', 'sole', 'multiple', 'ample', 'simple', 'supple', 'purple', 'subtle', 'gentle', 'little', 'miniscule', 'homestyle', 'lame', 'same', 'pro-same', 'tame', 'creme', 'supreme', 'extreme', 'prime', 'maritime', 'welcome', 'handsome', 'troublesome', 'wholesome', 'awesome', 'worrisome', 'burdensome', 'humane', 'insane', 'fine', 'online', 'philippine', 'Alexandrine', 'genuine', 'equine', 'done', 'gone', 'lone', 'alone', 'prone', 'bare', 'rare', 'aware', 'unaware', 'mediocre', 'sincere', 'mere', 'severe', 'dire', 'entire', 'hardcore', 'afore', 'offshore', 'more', 'secure', 'insecure', 'obscure', 'pure', 'sure', 'unsure', 'mature', 'premature', 'please', 'Portugese', 'Sinhalese', 'Nepalese', 'Siamese', 'Vietnamese', 'Lebanese', 'Japanese', 'Taiwanese', 'Chinese', 'precise', 'wise', 'false', 'else', 'dense', 'immense', 'commonsense', 'tense', 'intense', 'close', 'loose', 'suppose', 'adverse', 'diverse', 'obtuse', 'delicate', 'aggregate', 'immediate', 'intermediate', 'appropriate', 'inappropriate', 'late', 'legitimate', 'ultimate', 'intimate', 'approximate', 'effeminate', 'dominate', 'peregrinate', 'compassionate', 'affectionate', 'disproportionate', 'fortunate', 'unfortunate', 'separate', 'desparate', 'deliberate', 'inconsiderate', 'moderate', 'degenerate', 'seperate', 'desperate', 'literate', 'irate', 'elaborate', 'corporate', 'accurate', 'intrastate', 'undergraduate', 'adequate', 'private', 'complete', "shi'ite", 'white', 'Shiite', 'anti-Shiite', 'elite', 'polite', 'impolite', 'definite', 'indefinite', 'infinite', 'favorite', 'favourite', 'exquisite', 'opposite', 'tripartite', 'remote', 'cute', 'dilute', 'absolute', 'due', 'overdue', 'vague', 'blue', 'unique', 'antique', 'holocaust-esque', 'grotesque', 'true', 'untrue', 'rave', 'brave', 'naive', 'live', 'alive', 'abrasive', 'persuasive', 'invasive', 'cohesive', 'repulsive', 'defensive', 'offensive', 'comprehensive', 'apprehensive', 'expensive', 'inexpensive', 'intensive', 'extensive', 'responsive', 'unresponsive', 'massive', 'recessive', 'aggressive', 'progressive', 'impressive', 'oppressive', 'permissive', 'reclusive', 'inclusive', 'combative', 'communicative', 'provocative', 'creative', 'negative', 'investigative', 'legislative', 'speculative', 'affirmative', 'informative', 'lucrative', 'imperative', 'administrative', 'authoritative', 'argumentative', 'tentative', 'innovative', 'conservative', 'active', 'inactive', 'interactive', 'attractive', 'defective', 'effective', 'ineffective', 'semi-objective', 'selective', 'reflective', 'collective', 'despective', 'respective', 'protective', 'addictive', 'distinctive', 'reproductive', 'counterproductive', 'destructive', 'instructive', 'constructive', 'secretive', 'primitive', 'definitive', 'inquisitive', 'sensitive', 'insensitive', 'positive', 'competitive', 'intuitive', 'substantive', 'attentive', 'preventive', 'captive', 'receptive', 'descriptive', 'prescriptive', 'disruptive', 'supportive', 'executive', 'above', 'brief', 'waterproof', 'dwarf', 'eg', 'non-veg', 'big', 'probing', 'absorbing', 'disturbing', 'convincing', 'misleading', 'outstanding', 'condescending', 'resounding', 'astounding', 'rewarding', 'damaging', 'discouraging', 'challenging', 'nourishing', 'distinguishing', 'soothing', 'heartbreaking', 'breathtaking', 'shocking', 'fucking', 'looking', 'revealing', 'rambling', 'troubling', 'freewheeling', 'grueling', 'compelling', 'filling', 'willing', 'startling', 'bustling', 'belittling', 'dazzling', 'calming', 'overwhelming', 'forthcoming', 'welcoming', 'upcoming', 'charming', 'alarming', 'heartwarming', 'frightening', 'remaining', 'entertaining', 'defining', 'stunning', 'functioning', 'concerning', 'ongoing', 'sweeping', 'anti-shipping', 'caring', 'uncaring', 'overbearing', 'spacefaring', 'glaring', 'inspiring', 'boring', 'pleasing', 'surprising', 'imposing', 'embarrassing', 'depressing', 'missing', 'discussing', 'confusing', 'amusing', 'intoxicating', 'intimidating', 'accommodating', 'rejuvenating', 'fascinating', 'discriminating', 'frustrating', 'devastating', 'distracting', 'disrespecting', 'addicting', 'fleeting', 'pre-meeting', 'uplifting', 'exciting', 'insulting', 'disappointing', 'comforting', 'lasting', 'interesting', 'uninteresting', 'disgusting', 'upsetting', 'fitting', 'putting', 'loving', 'relaxing', 'dying', 'terrifying', 'horrifying', 'gratifying', 'satisfying', 'underlying', 'annoying', 'worrying', 'trying', 'amazing', 'agonizing', 'mesmerizing', 'appetizing', 'long', 'lifelong', 'strong', 'wrong', 'hung', 'young', 'smug', 'rich', 'French', 'much', 'such', 'meh', 'high', 'enough', 'rough', 'thorough', 'tough', 'awash', 'fresh', 'Swedish', 'childish', 'Kurdish', 'prudish', 'Turkish', 'hawkish', 'English', 'hellish', 'bullish', 'stylish', 'womanish', 'Spanish', 'cajunish', 'Irish', 'whitish', 'British', 'doltish', 'skittish', 'Scottish', 'Jewish', 'harsh', 'anti-bush', '50th', '5th', '25th', '18th', '19th', 'dth', 'nineteenth', 'smooth', 'worth', 'fourth', 'South', 'Thai', 'Wahhabi', 'Saudi', 'salafi', 'balochi', 'Bangladeshi', 'Israeli', 'anti-Israeli', 'semi', 'Pakistani', 'mini', 'Sunni', 'Iraqi', 'panjsheri', 'kuwaiti', 'neo-Nazi', 'bleak', 'seak', 'weak', 'blak', 'bareback', 'black', 'thick', 'slick', 'sick', 'quick', 'stuck', 'sleek', 'meek', 'Greek', 'blank', 'pink', 'drunk', 'dark', 'tribal', 'Global', 'global', 'farcical', 'radical', 'medical', 'methodical', 'magical', 'logical', 'idelogical', 'ecological', 'ideological', 'theological', 'psychological', 'biological', 'phenological', 'technological', 'neurological', 'surgical', 'liturgical', 'hierarchical', 'geographical', 'ethical', 'mythical', 'umbilical', 'psycholical', 'chemical', 'alchemical', 'biochemical', 'economical', 'technical', 'cynical', 'tropical', 'typical', 'numerical', 'hysterical', 'empirical', 'historical', 'electrical', 'asymmetrical', 'nonsensical', 'classical', 'musical', 'physical', 'mathematical', 'practical', 'tactical', 'political', 'socio-political', 'critical', 'identical', 'skeptical', 'optical', 'cortical', 'logistical', 'mystical', 'analytical', 'focal', 'local', 'fiscal', 'pyrimidal', 'bridal', 'ideal', 'real', 'legal', 'illegal', 'lethal', 'proverbial', 'racial', 'interracial', 'special', 'judicial', 'beneficial', 'unofficial', 'artificial', 'superficial', 'financial', 'provincial', 'social', 'non-social', 'commercial', 'non-commercial', 'crucial', 'parochial', 'aerial', 'imperial', 'senatorial', 'territorial', 'industrial', 'controversial', 'spatial', 'initial', 'substantial', 'confidential', 'residential', 'presidential', 'preferential', 'essential', 'non-essential', 'nonessential', 'potential', 'influential', 'intial', 'martial', 'partial', 'trivial', 'magickal', 'halal', 'minimal', 'optimal', 'thermal', 'formal', 'normal', 'abnormal', 'phenomenal', 'renal', 'final', 'original', 'marginal', 'seminal', 'criminal', 'spinal', 'optinal', 'regional', 'occasional', 'provisional', 'professional', 'unprofessional', 'congressional', 'educational', 'transformational', 'national', 'multi-national', 'international', 'rational', 'operational', 'aspirational', 'irrational', 'sensational', 'conversational', 'organizational', 'fractional', 'transactional', 'functional', 'cross-functional', 'dysfunctional', 'traditional', 'additional', 'nutritional', 'transitional', 'intentional', 'conventional', 'nonconventional', 'emotional', 'promotional', 'notional', 'exceptional', 'constitutional', 'seasonal', 'personal', 'interpersonal', 'maternal', 'internal', 'external', 'diurnal', 'nocturnal', 'municipal', 'liberal', 'federal', 'emphemeral', 'general', 'bilateral', 'several', 'integral', 'viral', 'behavioral', 'moral', 'electoral', 'central', 'procedural', 'inaugural', 'rural', 'natural', 'architectural', 'cultural', 'couter-cultural', 'scriptural', 'universal', 'causal', 'fatal', 'natal', 'neonatal', 'societal', 'digital', 'vital', 'dental', 'accidental', 'coincidental', 'mental', 'fundamental', 'nonjudgmental', 'experimental', 'detrimental', 'environmental', 'governmental', 'monumental', 'instrumental', 'continental', 'rental', 'parental', 'total', 'pivotal', 'mortal', 'postal', 'brutal', 'dual', 'residual', 'manual', 'annual', 'equal', 'visual', 'usual', 'unusual', 'actual', 'contractual', 'intellectual', 'punctual', 'spiritual', 'psycho-spiritual', 'eventual', 'virtual', 'mutual', 'sexual', 'bisexual', 'naval', 'medieval', 'loyal', 'parallel', 'cruel', 'Tamil', 'civil', 'normall', 'small', 'overall', 'tall', 'well', 'swell', 'ill', 'chill', 'brill', 'shrill', 'dull', 'full', 'succesfull', 'officiol', 'cool', 'awol', 'peaceful', 'graceful', 'forceful', 'prideful', 'shameful', 'hopeful', 'careful', 'useful', 'hateful', 'grateful', 'deliteful', 'tasteful', 'meaningful', 'watchful', 'faithful', 'youthful', 'bountiful', 'beautiful', 'thankful', 'painful', 'helpful', 'tearful', 'wonderful', 'powerful', 'colorful', 'flavorful', 'colourful', 'successful', 'unsuccessful', 'stressful', 'respectful', 'delightful', 'restful', 'awful', 'unlawful', 'post-saddam', 'mainstream', 'downstream', 'Moslem', 'non-Moslem', 'Muslim', 'anti-Muslim', 'interim', 'grim', 'calm', 'random', 'warm', 'maximum', 'urban', 'suburban', 'Cuban', 'Jamaican', 'Republican', 'American', 'anti-American', 'African', 'Mexican', 'caribbean', 'Carribean', 'lean', 'clean', 'Chilean', 'Mediterranean', 'European', 'Shakespearean', 'pagan', 'vegan', 'Afghan', 'Arabian', 'Trinidadian', 'Canadian', 'Indian', 'anti-Indian', 'Norwegian', 'Belgian', 'Australian', 'Italian', 'Sicilian', 'Brazilian', 'orwellian', 'Mongolian', 'Albanian', 'Jordanian', 'Iranian', 'Argentinian', 'Palestinian', 'pro-Palestinian', 'bosnian', 'brownian', 'humanatarian', 'sectarian', 'vegetarian', 'totalitarian', 'humanitarian', 'authoritarian', 'Syrian', 'Asian', 'Caucasian', 'Parisian', 'Russian', 'Malaysian', 'Egyptian', 'Christian', 'avian', 'fallujan', 'arakan', 'lankan', 'alaskan', 'Venezuelan', 'German', 'human', 'non-human', 'inhuman', 'spartan', 'gargantuan', 'moldovan', 'texan', 'Libyan', 'crowleyan', 'Aryan', 'laden', 'forbidden', 'hidden', 'downtrodden', 'sudden', 'golden', 'wooden', 'keen', 'green', 'mistaken', 'stricken', 'drunken', 'unspoken', 'broken', 'heartbroken', 'open', 'barren', 'molten', 'handwritten', 'rotten', 'uneven', 'brazen', 'frozen', 'foreign', 'benign', 'plain', 'main', 'certain', 'uncertain', 'vain', 'thin', 'akin', 'freakin', 'non-hodgkin', 'admin', 'Latin', 'latin', 'on', 'multi-nation', 'common', 'uncommon', 'mormon', 'soon', 'Saxon', 'modern', 'northern', 'southern', 'eastern', 'northeastern', 'southeastern', 'western', 'southwestern', 'born', 'newborn', 'worn', 'Pashtun', 'own', 'known', 'unknown', 'brown', 'ingrown', 'melo', 'solo', 'Filipino', 'latino', 'macro', 'metro', 'so', 'cheap', 'deep', 'steep', 'anti-ship', 'damp', 'limp', 'post-op', 'top', 'sharp', 'crisp', 'sq', 'dear', 'clear', 'unclear', 'nuclear', 'near', 'rear', 'far', 'familiar', 'similar', 'stellar', 'polar', 'solar', 'spectacular', 'secular', 'extracurricular', 'particular', 'circular', 'glandular', 'regular', 'singular', 'cellular', 'popular', 'unpopular', 'lunar', 'sub-par', 'subpar', 'Bolivar', 'pre-war', 'post-war', 'antiwar', 'micro-fiber', 'wider', 'under', 'sheer', 'eager', 'meager', 'kosher', 'together', 'other', 'further', 'earlier', 'premier', 'former', 'inner', 'proper', 'upper', 'luster', 'lackluster', 'latter', 'better', 'bitter', 'utter', 'outer', 'over', 'lower', 'fair', 'unfair', 'senior', 'junior', 'inferior', 'superior', 'ulterior', 'prior', 'major', 'minor', 'indoor', 'outdoor', 'poor', 'sr', 'sour', 'overseas', 'mis', 'upstairs', 'mass', 'excess', 'less', 'needless', 'endless', 'homeless', 'hopeless', 'careless', 'wireless', 'noiseless', 'senseless', 'useless', 'tasteless', 'clueless', 'worthless', 'ruthless', 'hookless', 'harmless', 'painless', 'expressionless', 'motionless', 'carless', 'flavorless', 'relentless', 'pointless', 'countless', 'heartless', 'lawless', 'flawless', 'express', 'Swiss', 'poss', 'gross', 'nuts', 'bogus', 'tremendous', 'horrendous', 'outrageous', 'gorgeous', 'miscellaneous', 'simultaneous', 'spontaneous', 'cutaneous', 'courteous', 'discourteous', 'amphibious', 'dubious', 'spacious', 'gracious', 'precious', 'delicious', 'suspicious', 'vicious', 'unconcious', 'conscious', 'insidious', 'religious', 'prestigious', 'harmonious', 'various', 'serious', 'mysterious', 'curious', 'furious', 'injurious', 'luxurious', 'rambunctious', 'ambitious', 'conscientious', 'unpretentious', 'contentious', 'scrumptious', 'cautious', 'obvious', 'previous', 'oblivious', 'anxious', 'jealous', 'marvelous', 'fabulous', 'rediculous', 'ridiculous', 'meticulous', 'famous', 'polygamous', 'autonomous', 'enormous', 'anonymous', 'mountainous', 'ominous', 'monotonous', 'cancerous', 'murderous', 'dangerous', 'numerous', 'generous', 'boisterous', 'preposterous', 'rigorous', 'disastrous', 'adventurous', 'solicitous', 'vacuous', 'strenuous', 'nervous', 'sus', 'neat', 'great', 'fat', 'phat', 'flat', 'nat', 'compact', 'exact', 'perfect', 'select', 'direct', 'correct', 'incorrect', 'strict', 'distinct', 'extinct', 'defunct', 'conjunct', 'sweet', 'quiet', 'midmarket', 'secret', 'unset', 'upset', 'wet', 'left', 'soft', 'non-microsoft', 'straight', 'slight', 'right', 'bright', 'alright', 'outright', 'tight', 'fraught', 'implicit', 'complicit', 'legit', 'difficult', 'significant', 'dependant', 'gant', 'elegant', 'arrogant', 'trenchant', 'valiant', 'brilliant', 'vigilant', 'slant', 'pregnant', 'malignant', 'poignant', 'dominant', 'rampant', 'tolerant', 'ignorant', 'pleasant', 'unpleasant', 'reluctant', 'militant', 'hesitant', 'important', 'distant', 'instant', 'constant', 'relevant', 'irrelevant', 'bent', 'adjacent', 'decent', 'recent', 'beneficent', 'magnificent', 'innocent', 'fluorescent', 'post-accident', 'confident', 'evident', 'transcendent', 'dependent', 'independent', 'prudent', 'diligent', 'intelligent', 'urgent', 'efficient', 'inefficient', 'sufficient', 'proficient', 'ancient', 'convenient', 'inconvenient', 'impatient', 'equivalent', 'silent', 'excellent', 'violent', 'non-violent', 'succulent', 'virulent', 'multi-compartment', 'permanent', 'eminent', 'preeminent', 'imminent', 'prominent', 'pertinent', 'apparent', 'transparent', 'different', 'indifferent', 'inherent', 'incoherent', 'diffrent', 'current', 'recurrent', 'present', 'incompetent', 'potent', 'consistent', 'persistent', 'existent', 'nonexistent', 'affluent', 'frequent', 'subsequent', 'eloquent', 'quaint', 'succint', 'joint', 'excelnt', 'burnt', 'hot', 'apt', 'nondescript', 'prompt', 'bankrupt', 'corrupt', 'smart', 'covert', 'short', 'fisrt', 'outcast', 'east', 'least', 'fast', 'last', 'roast', 'past', 'vast', 'West', 'modest', 'manifest', 'honest', 'dishonest', 'pre-arrest', 'west', 'cubist', 'Baathist', 'populist', 'pro-Zionist', 'impressionist', 'communist', 'moist', 'leftist', 'baptist', 'lost', 'most', 'foremost', 'innermost', 'first', 'robust', 'anti-trust', 'uncut', 'shut', 'about', 'devout', 'next', 'hindu', 'raw', 'few', 'new', 'low', 'below', 'shallow', 'fellow', 'yellow', 'slow', 'narrow', 'lax', 'intra-day', 'gay', 'anti-gay', 'okay', 'lay', 'gray', 'underway', 'nearby', 'spicy', 'pricy', 'juicy', 'fancy', 'bouncy', 'ready', 'bready', 'steady', 'unsteady', 'shady', 'giddy', 'shoddy', 'greedy', 'tidy', 'handy', 'spendy', 'windy', 'bloody', 'wordy', 'pricey', 'key', 'motley', 'homey', 'phoney', 'grey', 'mousey', 'fluffy', 'comfy', 'goofy', 'dodgy', 'dingy', 'spongy', 'churchy', 'scratchy', 'sketchy', 'itchy', 'shy', 'flashy', 'trashy', 'mushy', 'pushy', 'lengthy', 'healthy', 'unhealthy', 'wealthy', 'filthy', 'worthy', 'untrustworthy', 'diy', 'leaky', 'freaky', 'squeaky', 'shaky', 'tacky', 'gimmicky', 'picky', 'tricky', 'rocky', 'lucky', 'milky', 'spooky', 'pesky', 'non-crumbly', 'deadly', 'cuddly', 'worldly', 'friendly', 'unfriendly', 'kindly', 'cowardly', 'likely', 'unlikely', 'timely', 'homely', 'lonely', 'lovely', 'gangly', 'ugly', 'deathly', 'monthly', 'earthly', 'daily', 'oily', 'prickly', 'weekly', 'eventually', 'silly', 'heavenly', 'only', 'holy', 'early', 'yearly', 'quarterly', 'severly', 'neighborly', 'poorly', 'curly', 'hourly', 'surly', 'saintly', 'costly', 'ghostly', 'unruly', 'slimy', 'grimy', 'yummy', 'gloomy', 'anti-army', 'many', 'intercompany', 'tiny', 'skinny', 'funny', 'sunny', 'stony', 'thorny', 'creepy', 'dumpy', 'happy', 'unhappy', 'crappy', 'choppy', 'crispy', 'scary', 'secondary', 'primary', 'ordinary', 'extraordinary', 'imaginary', 'preliminary', 'urinary', 'revolutionary', 'temporary', 'contemporary', 'contrary', 'nessasary', 'necessary', 'unnecessary', 'proprietary', 'planetary', 'military', 'evidentary', 'parliamentary', 'elementary', 'wary', 'dry', 'feathery', 'watery', 'very', 'every', 'angry', 'hungry', 'sensory', 'laudatory', 'conciliatory', 'circulatory', 'regulatory', 'inflammatory', 'discriminatory', 'migratory', 'excitatory', 'satisfactory', 'inhibitory', 'sorry', 'furry', 'easy', 'uneasy', 'greasy', 'noisy', 'cosy', 'rosy', 'classy', 'messy', 'fussy', 'artsy', 'busy', 'lousy', 'thrifty', 'mighty', 'pre-university', 'salty', 'guilty', 'faulty', 'snooty', 'empty', 'dirty', 'flirty', 'nasty', 'tasty', 'feisty', 'touristy', 'dusty', 'trusty', 'ratty', 'pretty', 'shitty', 'heavy', 'wavy', 'chewy', 'sexy', 'lazy', 'crazy', 'cozy', 'dizzy', 'fuzzy', 'post-chavez']

ADJS = set(map(str.lower, ADJS))
# ensure cardinal directions are consistent
for x in ['north','south','east','west','northeast','northwest','southeast','southwest']:
    if x in ADJS:
        ADJS.remove(x)  # not sure whether these should be considered adjectives
for x in ['northern','southern','eastern','western','northeastern','northwestern','southeastern','southwestern']:
    ADJS.add(x)

# some things in the data missed by above heuristic: demonyms, etc. found by suffixes
for x in ["ba'athist",'fundamentalist','methodist','zionist','finest','advisory','alternative','atomic','botanical','cognitive','diagnostic','disposable','expeditionary','ferrous','greater','middle','nordic','poisonous','prudential','royal','royale','scrummy','super','transcendental','unitary','veterinary','nationwide','polish','czech']:
    ADJS.add(x)

ORDINALS = {'10th', '13th', '14th', '18th', '19th', '1st', '20th', '21st', '22nd', '23rd', '25th', '2nd', '3rd', '4th', '50th', '55th', '5th', '6th', '7th', 'fifth', 'first', 'fourth', 'second', 'sixth', 'third'}

# forms that show up in EWT more often as comparative ADJs than NOUN
CMPS = {'more', 'worse', 'nicer', 'broader', 'badder', 'wider', 'older', 'bolder', 'colder', 'harder', 'weirder', 'ruder', 'safer', 'bigger', 'longer', 'stronger', 'younger', 'larger', 'higher', 'smoother', 'pricier', 'windier', 'healthier', 'friendlier', 'earlier', 'happier', 'easier', 'busier', 'dirtier', 'heavier', 'crazier', 'thicker', 'darker', 'smaller', 'taller', 'cooler', 'simpler', 'warmer', 'sooner', 'cheaper', 'deeper', 'clearer', 'eaiser', 'wiser', 'closer', 'lesser', 'greater', 'later', 'quieter', 'lighter', 'tighter', 'smarter', 'faster', 'better', 'wetter', 'hotter', 'fewer', 'newer', 'lower', 'slower', 'less'}

# TODO: plain numerals as compound modifiers are mostly things like model names. maybe they should be NUM?

# TODO: manually fix existing PROPN amods

# forms that show up in EWT more often as VERB attaching as amod than NOUN
VERBS = {'f*ed', 'combed', 'displaced', 'paced', 'priced', 'enhanced', 'referenced', 'forced', 'sourced', 'reduced', 'induced', 'added', 'embedded', 'shredded', 'needed', 'divided', 'folded', 'sanded', 'recommended', 'intended', 'attended', 'extended', 'funded', 'surrounded', 'blooded', 'bearded', 'agreed', 'guaranteed', 'caged', 'packaged', 'damaged', 'vintaged', 'alleged', 'clogged', 'forged', 'attached', 'pitched', 'botched', 'brainwashed', 'established', 'published', 'finished', 'cherished', 'crushed', 'liquefied', 'specified', 'modified', 'gentrified', 'atrophied', 'implied', 'accompanied', 'occupied', 'dried', 'fried', 'married', 'tied', 'baked', 'backed', 'packed', 'cracked', 'checked', 'picked', 'fucked', 'ranked', 'linked', 'cooked', 'undercooked', 'overcooked', 'overlooked', 'invoked', 'provoked', 'marked', 'asked', 'led', 'sealed', 'mislabeled', 'failed', 'filed', 'boiled', 'foiled', 'called', 'propelled', 'filled', 'skilled', 'grilled', 'rolled', 'controlled', 'crumpled', 'scheduled', 'steamed', 'named', 'misnamed', 'proclaimed', 'confirmed', 'assumed', 'orphaned', 'screened', 'strengthened', 'blackened', 'darkened', 'heightened', 'designed', 'trained', 'combined', 'defined', 'redlined', 'blacklined', 'canned', 'planned', 'mentioned', 'imprisoned', 'owned', 'shaped', 'wrapped', 'stepped', 'equipped', 'seared', 'shared', 'prepared', 'crossbred', 'ordered', 'sponsered', 'registered', 'administered', 'neutered', 'fired', 'inspired', 'desired', 'retired', 'acquired', 'required', 'sponsored', 'deferred', 'preferred', 'injured', 'structured', 'based', 'encased', 'released', 'increased', 'purchased', 'disenfranchised', 'legalised', 'promised', 'summarised', 'advised', 'revised', 'convulsed', 'licensed', 'rinsed', 'closed', 'diagnosed', 'proposed', 'exposed', 'processed', 'repressed', 'oppressed', 'used', 'accused', 'focused', 'confiscated', 'updated', 'repeated', 'created', 'associated', 'negotiated', 'related', 'inflated', 'mutilated', 'contemplated', 'regulated', 'populated', 'estimated', 'designated', 'coordinated', 'contaminated', 'dominated', 'terminated', 'anticipated', 'rated', 'incorporated', 'annotated', 'stated', 'aggravated', 'elevated', 'enacted', 'affected', 'projected', 'elected', 'respected', 'suspected', 'expected', 'detected', 'convicted', 'completed', 'handcrafted', 'awaited', 'inhabited', 'prohibited', 'incited', 'limited', 'invited', 'planted', 'wanted', 'scented', 'documented', 'minted', 'printed', 'discounted', 'noted', 'accepted', 'inverted', 'reported', 'purported', 'roasted', 'wasted', 'suggested', 'requested', 'listed', 'posted', 'defrosted', 'rusted', 'trusted', 'executed', 'substituted', 'continued', 'microwaved', 'derived', 'dissolved', 'approved', 'observed', 'thawed', 'outlawed', 'renewed', 'screwed', 'towed', 'faxed', 'indexed', 'fixed', 'mixed', 'spayed', 'seized', 'localized', 'personalized', 'recognized', 'authorized', 'pressurized', 'made', 'see', 'done', 'grabbing', 'rubbing', 'numbing', 'producing', 'leading', 'raiding', 'abiding', 'sliding', 'balding', 'expanding', 'binding', 'surronding', 'surrounding', 'raging', 'ranging', 'emerging', 'refreshing', 'crushing', 'seething', 'frothing', 'speaking', 'fucking', 'ranking', 'provoking', 'working', 'failing', 'coming', 'looming', 'blooming', 'waning', 'strengthening', 'worsening', 'threatening', 'remaining', 'defining', 'reclining', 'winning', 'functioning', 'burning', 'going', 'soaring', 'differing', 'gathering', 'flickering', 'festering', 'retiring', 'neighboring', 'concurring', 'neighbouring', 'torturing', 'rising', 'losing', 'missing', 'causing', 'incubating', 'escalating', 'alternating', 'floating', 'deteriorating', 'connecting', 'conflicting', 'skyrocketing', 'competing', 'inciting', 'resulting', 'consenting', 'dissenting', 'reverting', 'supporting', 'lasting', 'existing', 'emitting', 'polluting', 'continuing', 'saving', 'arriving', 'glowing', 'following', 'growing', 'burrowing', 'paying', 'dying', 'lying', 'flying', 'sizing', 'stuck', 'spoken', 'broken', 'stolen', 'chosen', 'written', 'given', 'driven', 'proven', 'frozen', 'born', 'torn', 'sworn', 'blown', 'known', 'grown', 'deep', 'fought', 'built', 'kept', 'pre-cut'}

# default to ADJ if the word occurs as both ADJ and VERB in the corpus
VERBS -= ADJS

# add a few -ing/-ed forms
VERBS |= {'breaking','governing','rolling','applied','deemed','demented'}

# lemmas that show up in EWT more often as ADV than as NOUN or ADJ
ADVS = {'kinda', 'mega', 'aka', 'ultra', 'versa', 'eva', 'dab', 'ahead', 'instead', 'abroad', 'indeed', 'inland', 'behind', 'arond', 'beyond', 'around', 'aboard', 'onboard', 'northward', 'backward', 'onward', 'foward', 'afterward', 'forward', 'maybe', 'anyplace', 'twice', 'hence', 'since', 'once', 'aside', 'inside', 'outside', 'worldwide', 'nationwide', 'the', 'ie', 'unarguable', 'awhile', 'meanwhile', 'sometime', 'longtime', 'fulltime', 'overtime', 'anytime', 'some', 'offline', 'alone', 'here', 'there', 'where', 'somewhere', 'elsewhere', 'nowhere', 'anywhere', 'everywhere', 'were', 'before', 'therefore', 'onshore', 'furthermore', 'anymore', 'pre', 'career-wise', 'likewise', 'elsewise', 'otherwise', 'incomplete', 'quite', 'enroute', 'irrespective', 'above', 'def', 'off', 'itself', 'of', 'according', 'spanking', 'ling', 'during', 'spitting', 'long', 'along', 'tbh', 'much', 'though', 'although', 'through', 'oh', 'underneath', 'fifth', 'with', 'herewith', 'both', 'forth', 'fyi', 'onpeak', 'back', 'bareback', 'smack', 'stil', 'all', 'post-call', 'overall', 'well', 'downhill', 'still', 'them', 'seldom', 'from', 'atm', 'than', 'between', 'then', 'when', 'often', 'even', 'in', 'again', 'herein', 'wherein', 'damn', 'on', 'non', 'soon', 'down', 'ago', 'imo', 'no', 'too', 'so', 'moreso', 'also', 'to', 'pronto', 'asap', 'non-stop', 'esp', 'up', 'far', 'rather', 'together', 'altogether', 'either', 'further', 'earlier', 'sooner', 'super', 'later', 'after', 'thereafter', 'better', 'ever', 'never', 'whenever', 'whatsoever', 'wherever', 'forever', 'however', 'over', 'moreover', 'for', 'as', 'whereas', 'overseas', 'inwards', 'onwards', 'afterwards', 'besides', 'sometimes', 'is', 'this', 'perhaps', 'downstairs', 'upstairs', 'indoors', 'outdoors', 'regardless', 'nonetheless', 'nevertheless', 'across', 'thus', 'nowadays', 'aways', 'always', 'anyways', 'at', 'that', 'somewhat', 'collect', 'yet', 'overnight', 'right', 'downright', 'tilt', 'pursuant', 'alot', 'not', 'apart', 'atleast', 'most', 'almost', 'just', 'but', 'out', 'about', 'how', 'somehow', 'below', 'bellow', 'now', 'btw', 'ftw', 'approx', 'away', 'halfway', 'alway', 'anyway', 'by', 'hereby', 'thereby', 'already', 'hardy', 'likley', 'theraphy', 'why', 'literaly', 'probably', 'understandably', 'unspeakably', 'remarkably', 'presumably', 'unquestionably', 'reasonably', 'considerably', 'preferably', 'suitably', 'inevitably', 'notably', 'comfortably', 'unbelievably', 'conceivably', 'incredibly', 'terribly', 'horribly', 'possibly', 'superbly', 'publicly', 'badly', 'gladly', 'allegedly', 'markedly', 'supposedly', 'repeatedly', 'undoubtedly', 'expectedly', 'unexpectedly', 'wholeheartedly', 'reportedly', 'purportedly', 'admittedly', 'rapidly', 'wildly', 'kindly', 'blindly', 'secondly', 'profoundly', 'hardly', 'thirdly', 'loudly', 'nicely', 'scarcely', 'decidely', 'widely', 'rudely', 'freely', 'safely', 'largely', 'solely', 'extremely', 'handsomely', 'serenely', 'routinely', 'genuinely', 'barely', 'rarely', 'squarely', 'sincerely', 'merely', 'severely', 'entirely', 'securely', 'purely', 'surely', 'prematurely', 'precisely', 'densely', 'immensely', 'closely', 'purposely', 'delicately', 'immediately', 'appropriately', 'inappropriately', 'lately', 'immaculately', 'legitimately', 'ultimately', 'intimately', 'approximately', 'definately', 'indescriminately', 'indiscriminately', 'fortunately', 'unfortunately', 'separately', 'deliberately', 'desperately', 'accurately', 'adequately', 'privately', 'completely', 'incompletely', 'politely', 'definitely', 'indefinitely', 'acutely', 'absolutely', 'uniquely', 'bravely', 'decisively', 'aggressively', 'exclusively', 'relatively', 'collaboratively', 'figuratively', 'quantitatively', 'actively', 'effectively', 'objectively', 'collectively', 'respectively', 'cognitively', 'intuitively', 'briefly', 'accordingly', 'strikingly', 'willingly', 'seemingly', 'overwhelmingly', 'increasingly', 'surprisingly', 'imposingly', 'disgustingly', 'unwittingly', 'knowingly', 'amazingly', 'strongly', 'highly', 'roughly', 'thoroughly', 'freshly', 'feverishly', 'harshly', 'smoothly', 'steadily', 'handily', 'luckily', 'happily', 'primarily', 'summarily', 'customarily', 'ordinarily', 'extraordinarily', 'temporarily', 'necessarily', 'militarily', 'voluntarily', 'easily', 'heavily', 'quickly', 'frankly', 'sporadically', 'periodically', 'specifically', 'surgically', 'chemically', 'rhythmically', 'economically', 'mechanically', 'technically', 'ethnically', 'ironically', 'electronically', 'typically', 'categorically', 'historically', 'geometrically', 'basically', 'physically', 'emphatically', 'dramatically', 'thematically', 'automatically', 'democratically', 'bureaucratically', 'practically', 'genetically', 'politically', 'sarcastically', 'enthusiastically', 'drastically', 'simplistically', 'paradoxically', 'locally', 'ideally', 'fineally', 'really', 'legally', 'especially', 'officially', 'financially', 'socially', 'cordially', 'initially', 'substantially', 'confidentially', 'exponentially', 'essentially', 'potentially', 'partially', 'formally', 'informally', 'normally', 'abnormally', 'finally', 'originally', 'occasionally', 'professionally', 'nationally', 'functionally', 'traditionally', 'additionally', 'compositionally', 'notionally', 'exceptionally', 'institutionally', 'constitutionally', 'personally', 'eternally', 'internally', 'principally', 'generally', 'literally', 'orally', 'centrally', 'naturally', 'universally', 'fatally', 'accidentally', 'mentally', 'environmentally', 'totally', 'gradually', 'individually', 'manually', 'continually', 'equally', 'natrually', 'usually', 'actually', 'eventually', 'virtually', 'mutually', 'sexually', 'royally', 'holly', 'wholly', 'fully', 'peacefully', 'hopefully', 'carefully', 'gratefully', 'faithfully', 'beautifully', 'dutifully', 'thankfully', 'wonderfully', 'successfully', 'respectfully', 'restfully', 'actully', 'dimly', 'randomly', 'warmly', 'lukewarmly', 'firmly', 'suddenly', 'keenly', 'openly', 'evenly', 'mainly', 'certainly', 'only', 'sternly', 'cheaply', 'deeply', 'simply', 'clearly', 'nearly', 'similarly', 'spectacularly', 'particularly', 'regularly', 'popularly', 'properly', 'utterly', 'cleverly', 'overly', 'fairly', 'poorly', 'relentlessly', 'grossly', 'outrageously', 'simultaneously', 'instantaneously', 'spaciously', 'deliciously', 'suspiciously', 'religiously', 'ingeniously', 'seriously', 'mysteriously', 'notoriously', 'ambitiously', 'expeditiously', 'obviously', 'previously', 'marvelously', 'fabulously', 'ridiculously', 'unanimously', 'vigorously', 'continuously', 'neatly', 'greatly', 'exactly', 'perfectly', 'directly', 'indirectly', 'correctly', 'incorrectly', 'strictly', 'succinctly', 'distinctly', 'quietly', 'secretly', 'swiftly', 'slightly', 'explicitly', 'significantly', 'abundantly', 'arrogantly', 'radiantly', 'predominantly', 'pleasantly', 'unpleasantly', 'blatantly', 'reluctantly', 'importantly', 'instantly', 'constantly', 'recently', 'confidently', 'evidently', 'independently', 'gently', 'urgently', 'efficiently', 'sufficiently', 'conveniently', 'impatiently', 'silently', 'excellently', 'vehemently', 'permanently', 'apparently', 'differently', 'currently', 'presently', 'patently', 'appartently', 'consistently', 'persistently', 'frequently', 'subsequently', 'consequently', 'succintly', 'jointly', 'bluntly', 'aptly', 'promptly', 'abruptly', 'partly', 'expertly', 'shortly', 'vastly', 'honestly', 'mostly', 'firstly', 'truly', 'newly', 'slowly', 'narrowly', 'any', 'very', 'every', 'pretty'}

ADVS -= {'up', 'than', 'beyond', 'all', 'nationwide'}

guaranteed_correct = 0
possibly_correct = 0
form_dict = defaultdict(int)

def no_error_int(val):
  try:
    return int(val)
  except ValueError as err:
    if '.' in val or '-' in val: return 0
    raise err

def fuzzy_match(string, comparison):
  string = string.lower()
  if string == comparison: return True
  if string == comparison.replace("'", "’"): return True
  if string == comparison.replace("'", "‘"): return True
  if string == comparison.replace("'", ""): return True
  if string == comparison.replace("'", "`"): return True
  return False

def fix_poses(graph, filename):
  global guaranteed_correct, possibly_correct, form_dict

  egraph = graph.enhancedgraph

  i = 1
  end = max([no_error_int(key) for key in graph.nodes.keys()])
  while i <= end:    # changed <= to < to keep SpaceAfter=No on the last word of the sentence (these were formerly manual_review sentences: see above)
    n = graph.nodes[str(i)]
    gov = graph.nodes[graph.get_gov(str(i))]
    rel = graph.get_gov_reln(str(i))
    if n.upos=='PROPN' and rel=='compound' and int(gov.index)>i and gov.upos=='PROPN':
        lemma = n.lemma.lower()
        newtag = 'N'
        if lemma in ORDINALS:
            newtag = 'O'
        elif lemma in CMPS:
            newtag = 'C'
        elif lemma in ADJS:
            newtag = 'A'
        elif lemma in VERBS:
            newtag = 'V'
        elif lemma in ADVS:
            newtag = 'R'

        # update tag & deprel
        if newtag=='R':
            assert n.features in ('Number=Sing','Number=Plur')
            n.features = '_'
            n.upos = 'ADV'
            e, = graph.incomingedges[str(i)]
            g,rel = e
            graph.incomingedges[str(i)] = {(g,'advmod')}
            e, = egraph.incomingedges[str(i)]
            g,rel = e
            egraph.incomingedges[str(i)] = {(g,'advmod')}
        elif newtag=='O':
            assert n.features in ('Number=Sing','Number=Plur')
            n.features = 'NumType=Ord'
            n.upos = 'ADJ'
            e, = graph.incomingedges[str(i)]
            g,rel = e
            graph.incomingedges[str(i)] = {(g,'amod')}
            e, = egraph.incomingedges[str(i)]
            g,rel = e
            egraph.incomingedges[str(i)] = {(g,'amod')}
            # if not n.lemma.istitle() and not n.lemma[0].isnumeric():
            #     print('Title-casing lemma: ', n.lemma)
            #     n.lemma = n.lemma.title()
            # if not gov.lemma.istitle():
            #     print('Title-casing lemma: ', gov.lemma)
            #     gov.lemma = gov.lemma.title()
        elif newtag=='C':
            assert n.features in ('Number=Sing','Number=Plur')
            n.features = 'Degree=Cmp'
            n.upos = 'ADJ'
            e, = graph.incomingedges[str(i)]
            g,rel = e
            graph.incomingedges[str(i)] = {(g,'amod')}
            e, = egraph.incomingedges[str(i)]
            g,rel = e
            egraph.incomingedges[str(i)] = {(g,'amod')}
            assert n.lemma.endswith('er')
            n.lemma = n.lemma[:-2]
            print('Lemmatized comparative to: ', n.lemma)
        elif newtag=='V':
            assert n.features in ('Number=Sing','Number=Plur'),n.features
            assert n.lemma.endswith(('ing','ed'))
            n.features = 'VerbForm=Ger' if n.lemma.endswith('ing') else 'Tense=Past|VerbForm=Part'
            n.upos = 'VERB'
            e, = graph.incomingedges[str(i)]
            g,rel = e
            graph.incomingedges[str(i)] = {(g,'amod')}
            e, = egraph.incomingedges[str(i)]
            g,rel = e
            egraph.incomingedges[str(i)] = {(g,'amod')}
            if n.lemma.endswith('ing'):
                n.lemma = n.lemma[:-3]
                print('Lemmatized as a verb: ', n.lemma)
            elif n.lemma.endswith('ied'):
                n.lemma = n.lemma[:-3] + 'y'
                print('Lemmatized as a verb: ', n.lemma)
            elif n.lemma.endswith('ed'):
                n.lemma = n.lemma[:-2]
                print('Lemmatized as a verb: ', n.lemma)
        elif newtag=='A':
            print(n.form+'/'+newtag, gov.form+'/N')
            assert n.form.lower()==n.lemma.lower()
            assert n.features in ('Number=Sing','Number=Plur')
            n.features = 'Degree=Pos'
            n.upos = 'ADJ'
            e, = graph.incomingedges[str(i)]
            g,rel = e
            graph.incomingedges[str(i)] = {(g,'amod')}
            e, = egraph.incomingedges[str(i)]
            g,rel = e
            egraph.incomingedges[str(i)] = {(g,'amod')}
        # if lemma in ADVS:
        #     print('>>>', lemma)
    # elif n.upos=='ADJ' and 'NumType=Ord' in n.features:
    #     ORDINALS.add(n.lemma.lower())

    if n.upos in ('NOUN','ADJ','ADV'): # and 'Degree=Cmp' in n.features: #or n.upos=='VERB' and rel=='amod':
        c[n.lemma.lower()][n.upos] += 1


    i += 1
        # graph.print_conllu(highlight=i)
        # possibly_correct += 1





#def load_graphs_from_file(base_path, filename):
def load_graphs_from_file(filename):
    read_filename = filename
    out_filename = read_filename+'.out'
    lines = []

    with open(read_filename, 'r') as f:
        with open(out_filename, 'w') as fout:
            for line in f:
                if line.strip() == "":
                    if len(lines) > 0:
                        graph = DependencyGraph(lines=lines)
                        if lines[0].split()[-1] in manual_review or lines[1].split()[-1] in manual_review:
                            print("Skipping for manual review:" + lines[0].strip())
                        else:
                            fix_poses(graph, filename)
                        graph.print_conllu(f=fout)
                    lines.clear()
                else:
                    lines.append(line)

    os.replace(out_filename, read_filename)

def load_for_all_in_directory(filepath):
    files = os.listdir(filepath)
    for filename in files:
        load_graphs_from_file(filepath, filename)

    # print("Guaranteed correct:", guaranteed_correct)
    # print("Others:", possibly_correct)
    # print(form_dict)

#load_for_all_in_directory(sys.argv[1])

for inFP in sys.argv[1:]:
    load_graphs_from_file(inFP)

# adjlist = set()
# for lemma,counts in c.items():
#     if len(lemma)>1 and '.' not in lemma and counts['ADV']>counts['NOUN'] and counts['ADV']>counts['ADJ']:
#         adjlist.add(lemma)
# print(sorted(adjlist, key=lambda x: ''.join(reversed(x))))
#print(sorted(ORDINALS))
