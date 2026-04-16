import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Users } from 'lucide-react';

const AI_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  'Claude':      { bg: '#FFF1E6', text: '#C05621', border: '#F6AD55' },
  'GPT-4o':      { bg: '#F0FFF4', text: '#276749', border: '#68D391' },
  'Gemini':      { bg: '#EBF8FF', text: '#2C5282', border: '#63B3ED' },
  'Perplexity':  { bg: '#FAF5FF', text: '#553C9A', border: '#B794F4' },
  'MiniMax':     { bg: '#F7FAFC', text: '#4A5568', border: '#CBD5E0' },
  'Haiku':       { bg: '#FFFFF0', text: '#744210', border: '#F6E05E' },
  'Opus':        { bg: '#FFF5F5', text: '#9B2335', border: '#FC8181' },
};

const A = {
  lion:     'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Lion.png',
  cat:      'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Cat.png',
  fox:      'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Fox.png',
  owl:      'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Owl.png',
  bear:     'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Bear.png',
  rabbit:   'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Rabbit%20Face.png',
  tiger:    'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Tiger.png',
  panda:    'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Panda.png',
  deer:     'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Deer.png',
  chipmunk: 'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Chipmunk.png',
  dog:      'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Dog.png',
  raccoon:  'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Raccoon.png',
  hamster:  'https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Animals/Hamster.png',
};

interface Member { name: string; role: string; image: string; ai: string; desc?: string; tasks?: string[]; }
interface ProjectTeam { id: string; name: string; status: '진행 중' | '완료' | '대기'; statusColor: string; members: Member[]; }

// ─── 고정 조직 ───────────────────────────────────────────
const boardMembers: Member[] = [
  {
    name: '시은', role: '오케스트레이터', image: A.cat, ai: 'Claude',
    desc: '이사팀 전체 흐름을 총괄. 리안의 아이디어를 구체화하고, 각 에이전트에게 역할을 배분한 뒤 결과물을 취합해 다음 단계로 넘긴다.',
    tasks: ['아이디어 명확화 인터뷰', '파이프라인 흐름 제어', '팀 설계 초안 작성'],
  },
  {
    name: '태호', role: '트렌드 스카우터', image: A.fox, ai: 'MiniMax',
    desc: '업계 트렌드를 실시간으로 수집. 리안의 아이디어가 시장 흐름과 맞는지 빠르게 판단할 수 있도록 배경 정보를 제공한다.',
    tasks: ['SNS·커뮤니티 트렌드 스캔', '유사 서비스 현황 파악', '트렌드 요약 리포트 생성'],
  },
  {
    name: '서윤', role: '시장 리서처', image: A.owl, ai: 'Perplexity',
    desc: 'Perplexity를 활용해 실시간 시장 데이터를 수집. 타겟 고객의 Pain Point, 시장 규모, 경쟁사 분석을 담당한다.',
    tasks: ['실시간 시장 규모 조사', '경쟁사 분석', '타겟 고객 Pain Point 발굴'],
  },
  {
    name: '민수', role: '전략가', image: A.bear, ai: 'GPT-4o',
    desc: 'GPT-4o로 비즈니스 전략을 수립. 린 캔버스 형식으로 수익 모델을 설계하고 LTV/CAC 등 핵심 지표를 계산한다.',
    tasks: ['린 캔버스 작성', '수익 모델 설계', 'LTV·CAC 계산 및 검증'],
  },
  {
    name: '하은', role: '검증관', image: A.rabbit, ai: 'Gemini',
    desc: 'Gemini로 팩트를 검증하고 반론을 제시. "이미 있는 서비스" 실제 사례를 찾아내고 리스크를 미리 드러낸다.',
    tasks: ['팩트 체크 및 반론 생성', '경쟁 서비스 실사례 제시', '리스크 시나리오 분석'],
  },
  {
    name: '준혁', role: '심판', image: A.tiger, ai: 'Claude',
    desc: 'Claude Sonnet 기반의 최종 GO/NO-GO 판단자. 이사팀 전체 논의를 종합해 사업화 여부를 결정한다.',
    tasks: ['GO / NO-GO 최종 판단', '이사팀 논의 종합 평가', '핵심 리스크 우선순위 정리'],
  },
];
const eduMembers: Member[] = [
  {
    name: '도윤', role: '교장', image: A.panda, ai: 'Gemini',
    desc: '새로운 팀이 생성될 때 커리큘럼을 설계하고 에이전트를 교육. 자료들/ 폴더에 넣은 파일을 읽고 지식 베이스에 저장한다.',
    tasks: ['신규 팀 커리큘럼 설계', '자료들/ 폴더 자동 처리', 'knowledge/base/ 지식 저장'],
  },
  {
    name: '서윤', role: '교관 겸직', image: A.owl, ai: 'Perplexity',
    desc: '이사팀 시장 리서처이자 교육팀 교관 겸직. Perplexity로 최신 지식을 수집해 팀 전체에 배포한다.',
    tasks: ['최신 트렌드 지식 수집', '팀별 지식 배포', '이사팀 리서치 겸직'],
  },
];
const analyticsMembers: Member[] = [
  {
    name: '지수', role: '비전 분석관', image: A.deer, ai: 'Gemini',
    desc: 'Gemini Vision으로 이미지·영상을 분석. 리안이 inbox에 넣은 스크린샷·영상을 자동으로 처리해 인사이트를 추출한다.',
    tasks: ['이미지·영상 자동 분석', 'knowledge/inbox/ 스캔', '비전 기반 인사이트 추출'],
  },
  {
    name: '재원', role: '리서처', image: A.chipmunk, ai: 'Perplexity',
    desc: 'Perplexity MCP로 경쟁사 랜딩 페이지를 스크랩하고 타겟 Pain Point를 실시간 조사. 마케팅 전략의 근거 데이터를 만든다.',
    tasks: ['경쟁사 랜딩 페이지 스크랩', 'Pain Point 실시간 조사', '시장·타겟 데이터 정리'],
  },
  {
    name: '승현', role: '전략가', image: A.dog, ai: 'Claude',
    desc: 'SPIN·Challenger 영업 기법으로 오프라인 영업 전략을 수립. 퍼널을 재설계하고 거절 처리 스크립트를 작성한다.',
    tasks: ['SPIN 영업 전략 수립', '퍼널 재설계', '거절 처리 시나리오 작성'],
  },
  {
    name: '예진', role: '카피라이터', image: A.cat, ai: 'Claude',
    desc: '소상공인 대상 DM·광고 카피·영업 스크립트를 작성. 승현의 전략을 실제 문장으로 구현한다.',
    tasks: ['DM·광고 카피 작성', '영업 스크립트 3버전 생성', '카카오·인스타 문구 최적화'],
  },
];
const ultraMembers: Member[] = [
  {
    name: '현우', role: 'CTO', image: A.bear, ai: 'Claude',
    desc: '기술 아키텍처와 스택을 결정. Wave 4에서 FE·BE 코드를 통합 리뷰하고 배포 전략을 수립한다.',
    tasks: ['기술 스택 결정', '코드 통합 리뷰', '배포 아키텍처 설계'],
  },
  {
    name: '나은', role: 'CDO', image: A.fox, ai: 'Claude',
    desc: 'Stitch MCP로 고품질 UI를 생성하고 DESIGN.md를 작성. FE 개발자가 바로 구현할 수 있도록 핸드오프 자료를 만든다.',
    tasks: ['Stitch로 UI 화면 생성', 'DESIGN.md 작성', 'FE 핸드오프 자료 제작'],
  },
  {
    name: '유진', role: 'PM', image: A.rabbit, ai: 'Haiku',
    desc: 'PRD를 태스크로 분해하고 User Story를 작성. FE·BE가 독립적으로 작업할 수 있도록 개발 우선순위를 정리한다.',
    tasks: ['User Story 작성', '태스크 분해 및 우선순위', '화면 플로우 정의'],
  },
  {
    name: '민준', role: 'FE', image: A.raccoon, ai: 'Haiku',
    desc: 'React/Next.js로 UI를 구현. 나은의 디자인과 백엔드 API를 연결하고 상태 관리까지 담당한다.',
    tasks: ['React 컴포넌트 구현', '백엔드 API 연결', '상태 관리 및 최적화'],
  },
  {
    name: '정우', role: 'BE', image: A.dog, ai: 'Haiku',
    desc: 'API를 설계하고 DB 스키마를 작성. Cloudflare Workers·D1 기반으로 비즈니스 로직을 구현한다.',
    tasks: ['REST API 설계', 'DB 스키마 작성', 'Cloudflare Workers 구현'],
  },
  {
    name: '소연', role: 'QA', image: A.hamster, ai: 'Haiku',
    desc: '테스트 전략을 수립하고 버그를 수정. 배포 전 리스크 맵을 작성해 E2E 품질을 보증한다.',
    tasks: ['테스트 시나리오 작성', '버그 수정 및 검증', 'E2E 배포 전 최종 확인'],
  },
  {
    name: '재현', role: 'Analytics', image: A.chipmunk, ai: 'Claude',
    desc: '배포 후 퍼널 분석을 수행. GA4·네이버 광고 데이터를 수집해 개선 우선순위를 정리하고 FE·BE에 수정을 지시한다.',
    tasks: ['퍼널 분석 및 성과 측정', '주간 성과 리포트 작성', 'FE·BE 개선 지시서 작성'],
  },
];

// 프로젝트팀 — 실제 연동 시 채워짐
const projectTeams: ProjectTeam[] = [];

// ─── 사무용품 컴포넌트 ────────────────────────────────────

const Plant = ({ label }: { label?: string }) => (
  <div className="flex flex-col items-center justify-end select-none" style={{ width: 48, height: 80 }}>
    <span className="text-3xl leading-none">🪴</span>
    {label && <span className="text-[7px] text-gray-400 mt-0.5">{label}</span>}
  </div>
);

const SmallPlant = () => (
  <div className="select-none text-xl leading-none self-end mb-1">🌿</div>
);

const CoffeeMachine = () => (
  <div className="flex flex-col items-center select-none self-end mb-1">
    <div className="w-8 h-10 bg-gray-700 rounded-t-lg rounded-b-sm flex flex-col items-center justify-center gap-0.5 shadow-md">
      <span className="text-[10px]">☕</span>
      <div className="w-4 h-1 bg-orange-400 rounded-full opacity-60"></div>
    </div>
    <span className="text-[7px] text-gray-400 mt-0.5">커피</span>
  </div>
);

const Bookshelf = () => (
  <div className="flex flex-col items-center select-none self-end mb-1">
    <div className="w-10 h-14 bg-amber-800 rounded-sm shadow-inner flex flex-col gap-0.5 p-0.5">
      {['bg-red-300','bg-blue-300','bg-green-300','bg-yellow-300','bg-purple-300'].map((c, i) => (
        <div key={i} className={`flex-1 ${c} rounded-sm opacity-80`}></div>
      ))}
    </div>
    <span className="text-[7px] text-gray-400 mt-0.5">책장</span>
  </div>
);

const Printer = () => (
  <div className="flex flex-col items-center select-none self-end mb-1">
    <div className="w-10 h-8 bg-gray-200 border border-gray-300 rounded-sm shadow flex items-center justify-center">
      <span className="text-[14px]">🖨️</span>
    </div>
    <span className="text-[7px] text-gray-400 mt-0.5">프린터</span>
  </div>
);

const MeetingTable = ({ seats = 4 }: { seats?: number }) => (
  <div className="flex flex-col items-center select-none self-end mb-2 mx-2">
    {/* Chairs top */}
    <div className="flex gap-2 mb-0.5">
      {Array.from({ length: Math.ceil(seats / 2) }).map((_, i) => (
        <div key={i} className="w-5 h-2.5 bg-gray-400/60 rounded-t-full border border-gray-400/40"></div>
      ))}
    </div>
    {/* Table */}
    <div className="bg-amber-700 rounded-xl shadow-lg flex items-center justify-center"
      style={{ width: Math.ceil(seats / 2) * 28 + 8, height: 44 }}>
      <div className="w-3/4 h-0.5 bg-amber-500/40 rounded-full"></div>
    </div>
    {/* Chairs bottom */}
    <div className="flex gap-2 mt-0.5">
      {Array.from({ length: Math.floor(seats / 2) }).map((_, i) => (
        <div key={i} className="w-5 h-2.5 bg-gray-400/60 rounded-b-full border border-gray-400/40"></div>
      ))}
    </div>
    <span className="text-[7px] text-gray-400 mt-1">회의 테이블</span>
  </div>
);

// ─── 책상 컴포넌트 (가구 느낌) ────────────────────────────

const AiBadge = ({ ai }: { ai: string }) => {
  const c = AI_COLORS[ai];
  if (!c) return null;
  return (
    <span style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
      className="text-[7px] border font-bold px-1 py-0.5 rounded-full leading-none">{ai}</span>
  );
};

const Desk = ({ member, onClick }: { member: Member; onClick: () => void }) => (
  <div onClick={onClick}
    className="flex flex-col items-center cursor-pointer group select-none"
    style={{ width: 72 }}>
    {/* 책상 상판 */}
    <div className="w-full rounded-t-lg shadow-md group-hover:shadow-lg transition-shadow relative overflow-hidden"
      style={{
        height: 64,
        background: 'linear-gradient(160deg, #fef3c7 0%, #fde68a 60%, #fbbf24 100%)',
        border: '1.5px solid #d97706',
      }}>
      {/* 모니터 */}
      <div className="absolute top-1.5 left-1/2 -translate-x-1/2 w-8 h-1.5 bg-gray-600 rounded-sm opacity-50"></div>
      {/* 아바타 */}
      <div className="absolute inset-0 flex items-center justify-center pt-2">
        <img src={member.image} alt={member.name}
          className="w-9 h-9 object-contain drop-shadow-sm group-hover:scale-110 transition-transform"
          referrerPolicy="no-referrer" />
      </div>
    </div>
    {/* 의자 */}
    <div className="w-10 h-2.5 rounded-b-full border-x border-b transition-colors"
      style={{ backgroundColor: '#9CA3AF80', borderColor: '#6B7280' }}></div>
    {/* 명패 */}
    <div className="mt-1.5 flex flex-col items-center gap-0.5">
      <span className="text-[11px] font-extrabold text-gray-800 leading-none">{member.name}</span>
      <span className="text-[8px] text-gray-400 text-center leading-tight">{member.role}</span>
      <AiBadge ai={member.ai} />
    </div>
  </div>
);

// CEO 전용 대형 책상
const CeoDesk = ({ onClick }: { onClick: () => void }) => (
  <div onClick={onClick} className="flex flex-col items-center cursor-pointer group select-none" style={{ width: 96 }}>
    <div className="w-full rounded-t-xl shadow-xl group-hover:shadow-2xl transition-shadow relative overflow-hidden"
      style={{
        height: 80,
        background: 'linear-gradient(160deg, #7c3aed 0%, #4c1d95 100%)',
        border: '2px solid #6d28d9',
      }}>
      <div className="absolute top-2 left-1/2 -translate-x-1/2 w-12 h-2 bg-purple-200 rounded-sm opacity-30"></div>
      <div className="absolute inset-0 flex items-center justify-center pt-3">
        <img src={A.lion} alt="리안" className="w-12 h-12 object-contain drop-shadow group-hover:scale-110 transition-transform"
          referrerPolicy="no-referrer" />
      </div>
    </div>
    <div className="w-14 h-3 rounded-b-full border-x border-b"
      style={{ backgroundColor: '#7C3AED40', borderColor: '#7C3AED' }}></div>
    <div className="mt-1.5 flex flex-col items-center gap-0.5">
      <span className="text-[13px] font-extrabold text-gray-900 leading-none">리안</span>
      <span className="text-[9px] text-purple-600 font-bold">CEO</span>
    </div>
  </div>
);

// ─── 방 타입 ─────────────────────────────────────────────

// 타일 패턴 배경
const tilePattern = `
  repeating-linear-gradient(
    0deg,
    transparent,
    transparent 19px,
    rgba(0,0,0,0.04) 19px,
    rgba(0,0,0,0.04) 20px
  ),
  repeating-linear-gradient(
    90deg,
    transparent,
    transparent 19px,
    rgba(0,0,0,0.04) 19px,
    rgba(0,0,0,0.04) 20px
  )
`;

interface RoomProps {
  title: string;
  subtitle?: string;
  wallColor: string;
  floorColor: string;
  children: React.ReactNode;
  className?: string;
}

const RoomShell = ({ title, subtitle, wallColor, floorColor, children, className = '' }: RoomProps) => (
  <div className={`relative rounded-2xl overflow-hidden flex flex-col ${className}`}
    style={{
      border: `3px solid ${wallColor}`,
      boxShadow: `inset 0 0 0 1.5px ${wallColor}30`,
    }}>
    {/* 방 간판 */}
    <div className="flex items-center gap-2 px-4 py-2 border-b"
      style={{ backgroundColor: wallColor + '18', borderColor: wallColor + '30' }}>
      <span className="font-extrabold text-[13px] tracking-tight" style={{ color: wallColor }}>{title}</span>
      {subtitle && <span className="text-[9px] text-gray-400 font-medium">{subtitle}</span>}
    </div>
    {/* 방 바닥 */}
    <div className="flex-1 p-4" style={{ backgroundColor: floorColor, backgroundImage: tilePattern }}>
      {children}
    </div>
  </div>
);

// ─── 개별 방들 ────────────────────────────────────────────

const CeoOffice = ({ onCeoClick }: { onCeoClick: () => void }) => (
  <RoomShell title="CEO 코너 오피스" wallColor="#7C3AED" floorColor="#F5F0FF">
    <div className="flex flex-col h-full gap-4">
      <div className="flex items-end gap-3">
        <Plant />
        <CeoDesk onClick={onCeoClick} />
        <Plant />
      </div>
      <div className="text-[9px] text-gray-400 leading-relaxed">
        <div>✦ 아이디어 최종 판단</div>
        <div>✦ GO / NO-GO 결정</div>
        <div>✦ 에이전트 피드백</div>
      </div>
    </div>
  </RoomShell>
);

const BoardRoom = ({ onMemberClick }: { onMemberClick: (m: Member) => void }) => (
  <RoomShell title="이사팀" subtitle="분석 + 팀 설계" wallColor="#3B82F6" floorColor="#EBF5FF">
    <div className="flex gap-3 items-end flex-wrap">
      <Plant />
      {boardMembers.slice(0, 3).map((m, i) => (
        <Desk key={i} member={m} onClick={() => onMemberClick(m)} />
      ))}
      <MeetingTable seats={4} />
      {boardMembers.slice(3).map((m, i) => (
        <Desk key={i} member={m} onClick={() => onMemberClick(m)} />
      ))}
      <SmallPlant />
    </div>
  </RoomShell>
);

const EducationRoom = ({ onMemberClick }: { onMemberClick: (m: Member) => void }) => (
  <RoomShell title="교육팀" subtitle="지식 관리" wallColor="#EAB308" floorColor="#FEFCE8">
    <div className="flex gap-3 items-end flex-wrap">
      <Bookshelf />
      {eduMembers.map((m, i) => (
        <Desk key={i} member={m} onClick={() => onMemberClick(m)} />
      ))}
      <Plant />
    </div>
  </RoomShell>
);

const AnalyticsRoom = ({ onMemberClick }: { onMemberClick: (m: Member) => void }) => (
  <RoomShell title="분석·마케팅팀" subtitle="비전분석 + 오프라인 영업" wallColor="#22C55E" floorColor="#F0FDF4">
    <div className="flex gap-3 items-end flex-wrap">
      <Plant />
      {analyticsMembers.slice(0, 2).map((m, i) => (
        <Desk key={i} member={m} onClick={() => onMemberClick(m)} />
      ))}
      <SmallPlant />
      {analyticsMembers.slice(2).map((m, i) => (
        <Desk key={i} member={m} onClick={() => onMemberClick(m)} />
      ))}
    </div>
  </RoomShell>
);

const UltraProductRoom = ({ onMemberClick }: { onMemberClick: (m: Member) => void }) => (
  <RoomShell title="UltraProduct팀" subtitle="코드 개발 실행 엔진" wallColor="#A855F7" floorColor="#FAF5FF">
    <div className="flex gap-3 items-end flex-wrap">
      <Plant />
      {ultraMembers.slice(0, 4).map((m, i) => (
        <Desk key={i} member={m} onClick={() => onMemberClick(m)} />
      ))}
      <div className="flex-grow" />
      <Printer />
    </div>
    <div className="flex gap-3 items-end flex-wrap mt-4">
      <SmallPlant />
      {ultraMembers.slice(4).map((m, i) => (
        <Desk key={i} member={m} onClick={() => onMemberClick(m)} />
      ))}
      <div className="flex-grow" />
      <CoffeeMachine />
    </div>
  </RoomShell>
);

// ─── 복도 ─────────────────────────────────────────────────
const Corridor = () => (
  <div className="h-10 flex items-center px-6 gap-4 rounded-xl"
    style={{
      background: 'repeating-linear-gradient(90deg, #e5e7eb 0px, #e5e7eb 30px, #f3f4f6 30px, #f3f4f6 60px)',
    }}>
    <div className="flex gap-2 items-center">
      <div className="w-2 h-2 rounded-full bg-green-400"></div>
      <span className="text-[10px] text-gray-500 font-bold">복도</span>
    </div>
    <Plant label="" />
    <Plant label="" />
  </div>
);

// ─── 프로젝트 사무실 (토글) ───────────────────────────────
const ProjectRoom = ({ project, onMemberClick }: {
  project: ProjectTeam;
  onMemberClick: (m: Member, teamName: string) => void;
}) => {
  const [open, setOpen] = useState(false);
  const statusColors: Record<string, string> = { '진행 중': '#22C55E', '완료': '#6B7280', '대기': '#F59E0B' };
  return (
    <div className="border-2 border-dashed rounded-2xl overflow-hidden"
      style={{ borderColor: statusColors[project.status] + '60', backgroundColor: open ? '#FAFAFA' : '#F8F9FA' }}>
      <button onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-5 py-4 hover:bg-gray-50 transition-colors">
        <span className="font-extrabold text-[14px] text-gray-800">{project.name}</span>
        <span className="text-[9px] font-bold px-2 py-0.5 rounded-full border"
          style={{ color: statusColors[project.status], borderColor: statusColors[project.status] + '66', backgroundColor: statusColors[project.status] + '15' }}>
          {project.status}
        </span>
        <span className="text-[11px] text-gray-400">{project.members.length}명</span>
        <div className="ml-auto text-gray-400">
          {open ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </div>
      </button>
      {open && (
        <div className="px-5 pb-5 pt-1" style={{ backgroundImage: tilePattern, backgroundColor: '#FAFAFA' }}>
          <div className="flex gap-3 items-end flex-wrap">
            <Plant />
            {project.members.map((m, i) => (
              <Desk key={i} member={m} onClick={() => onMemberClick(m, project.name)} />
            ))}
            <SmallPlant />
          </div>
        </div>
      )}
    </div>
  );
};

// ─── 사이드바 (전체 직원) ─────────────────────────────────
const allGroups = [
  { team: 'CEO', members: [{ name: '리안', role: 'CEO', image: A.lion, ai: 'Human' }] },
  { team: '이사팀', members: boardMembers },
  { team: '교육팀', members: eduMembers },
  { team: '분석·마케팅팀', members: analyticsMembers },
  { team: 'UltraProduct팀', members: ultraMembers },
];

const Sidebar = ({ open, onClose, onMemberClick }: {
  open: boolean; onClose: () => void; onMemberClick: (m: Member, t: string) => void;
}) => {
  const [expanded, setExpanded] = useState<string | null>(null);
  return (
    <>
      {open && <div className="fixed inset-0 bg-black/20 z-30" onClick={onClose} />}
      <div className={`fixed top-0 right-0 h-full w-68 bg-white shadow-2xl z-40 flex flex-col transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'}`}
        style={{ width: 260 }}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-gray-500" />
            <span className="font-extrabold text-[14px] text-gray-800">전체 직원</span>
            <span className="text-[11px] text-gray-400">
              {allGroups.reduce((s, g) => s + g.members.length, 0)}명
            </span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-[18px] font-bold leading-none">×</button>
        </div>
        <div className="flex-1 overflow-y-auto py-2">
          {allGroups.map(g => (
            <div key={g.team}>
              <button onClick={() => setExpanded(expanded === g.team ? null : g.team)}
                className="w-full flex items-center justify-between px-5 py-2.5 hover:bg-gray-50 transition-colors">
                <span className="text-[12px] font-bold text-gray-700">{g.team}</span>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-400">{g.members.length}명</span>
                  {expanded === g.team
                    ? <ChevronDown className="w-3 h-3 text-gray-400" />
                    : <ChevronRight className="w-3 h-3 text-gray-400" />}
                </div>
              </button>
              {expanded === g.team && (
                <div className="px-4 pb-2 flex flex-col gap-0.5">
                  {g.members.map((m, i) => (
                    <button key={i} onClick={() => onMemberClick(m, g.team)}
                      className="flex items-center gap-3 px-3 py-1.5 rounded-xl hover:bg-gray-100 transition-colors w-full text-left">
                      <img src={m.image} alt={m.name} className="w-8 h-8 object-contain" referrerPolicy="no-referrer" />
                      <div className="flex flex-col flex-1">
                        <span className="text-[12px] font-bold text-gray-800">{m.name}</span>
                        <span className="text-[10px] text-gray-400">{m.role}</span>
                      </div>
                      <AiBadge ai={m.ai} />
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

// ─── 모달 ─────────────────────────────────────────────────
const Modal = ({ member, teamName, onClose }: { member: Member; teamName: string; onClose: () => void }) => {
  const c = AI_COLORS[member.ai] || { bg: '#F7FAFC', text: '#4A5568', border: '#CBD5E0' };
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-3xl shadow-2xl w-80 overflow-hidden" onClick={e => e.stopPropagation()}>
        {/* 상단 헤더 */}
        <div className="flex items-center gap-4 p-6 pb-4" style={{ background: `linear-gradient(135deg, ${c.bg}, white)` }}>
          <img src={member.image} alt={member.name}
            className="w-20 h-20 object-contain drop-shadow-lg flex-shrink-0"
            referrerPolicy="no-referrer" />
          <div className="flex flex-col gap-1">
            <span className="text-[22px] font-extrabold text-gray-900 leading-none">{member.name}</span>
            <span className="text-[13px] font-bold text-gray-600">{member.role}</span>
            <span className="text-[10px] text-gray-400">{teamName}</span>
            <span style={{ backgroundColor: c.bg, color: c.text, borderColor: c.border }}
              className="border text-[9px] font-bold px-2 py-0.5 rounded-full w-fit mt-0.5">{member.ai}</span>
          </div>
        </div>

        <div className="px-6 pb-6 flex flex-col gap-4">
          {/* 한 줄 설명 */}
          {member.desc && (
            <div>
              <div className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">하는 일</div>
              <p className="text-[12px] text-gray-600 leading-relaxed">{member.desc}</p>
            </div>
          )}

          {/* 주요 업무 태스크 */}
          {member.tasks && member.tasks.length > 0 && (
            <div>
              <div className="text-[9px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">주요 업무</div>
              <div className="flex flex-col gap-1.5">
                {member.tasks.map((t, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: c.border }}></div>
                    <span className="text-[11px] text-gray-700">{t}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button onClick={onClose}
            className="mt-1 w-full py-2 rounded-xl text-[12px] font-bold text-gray-500 hover:bg-gray-100 transition-colors border border-gray-200">
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};

// ─── 메인 ────────────────────────────────────────────────
export default function App() {
  const [selected, setSelected] = useState<{ member: Member; teamName: string } | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const totalCount = allGroups.reduce((s, g) => s + g.members.length, 0);

  const onMember = (m: Member, teamName = '') => setSelected({ member: m, teamName });

  return (
    <div className="min-h-screen font-sans" style={{ backgroundColor: '#E8E4E0' }}>
      {/* 헤더 */}
      <header className="bg-white border-b border-gray-200 px-8 py-3 flex items-center gap-4 sticky top-0 z-20 shadow-sm">
        <img src={A.lion} alt="lion" className="w-8 h-8 drop-shadow-sm" referrerPolicy="no-referrer" />
        <div>
          <h1 className="text-[16px] font-extrabold text-[#5D4037] tracking-tight leading-none">LIAN COMPANY</h1>
          <p className="text-[10px] text-gray-400 font-medium">회사 사무실 — 2F</p>
        </div>
        <div className="ml-auto flex items-center gap-4">
          <span className="text-[11px] text-gray-400">총 {totalCount}명</span>
          <span className="w-2 h-2 rounded-full bg-green-400"></span>
          <span className="text-[11px] text-green-600 font-bold">운영 중</span>
          <button onClick={() => setSidebarOpen(o => !o)}
            className="flex items-center gap-1.5 bg-gray-900 text-white text-[11px] font-bold px-3 py-1.5 rounded-full hover:bg-gray-700 transition-colors">
            <Users className="w-3.5 h-3.5" />
            전체 직원
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-8 flex flex-col gap-4">

        {/* 상설 사무실 */}
        <div className="flex items-center gap-2 mb-1">
          <div className="w-1 h-4 bg-gray-400 rounded-full"></div>
          <span className="text-[11px] text-gray-500 font-bold uppercase tracking-widest">상설 사무실</span>
        </div>

        {/* 1층: CEO + 이사팀 + 교육팀 */}
        <div className="grid gap-4" style={{ gridTemplateColumns: '200px 1fr 240px' }}>
          <CeoOffice onCeoClick={() => onMember({ name: '리안', role: 'CEO', image: A.lion, ai: 'Human' }, 'CEO 코너 오피스')} />
          <BoardRoom onMemberClick={m => onMember(m, '이사팀')} />
          <EducationRoom onMemberClick={m => onMember(m, '교육팀')} />
        </div>

        {/* 복도 */}
        <Corridor />

        {/* 2층: 분석마케팅 + UltraProduct */}
        <div className="grid gap-4" style={{ gridTemplateColumns: '2fr 3fr' }}>
          <AnalyticsRoom onMemberClick={m => onMember(m, '분석·마케팅팀')} />
          <UltraProductRoom onMemberClick={m => onMember(m, 'UltraProduct팀')} />
        </div>

        {/* 프로젝트 사무실 섹션 */}
        <div className="flex items-center gap-2 mt-4 mb-1">
          <div className="w-1 h-4 bg-gray-400 rounded-full"></div>
          <span className="text-[11px] text-gray-500 font-bold uppercase tracking-widest">프로젝트 사무실</span>
          <span className="text-[10px] text-gray-400 bg-gray-200 px-2 py-0.5 rounded-full font-bold ml-1">
            {projectTeams.length > 0 ? `${projectTeams.length}개 진행` : '대기 중'}
          </span>
        </div>

        {projectTeams.length === 0 ? (
          <div className="border-2 border-dashed border-gray-300 rounded-2xl p-10 flex flex-col items-center gap-2 text-center"
            style={{ backgroundColor: '#F9F8F7' }}>
            <span className="text-3xl">🏗️</span>
            <span className="text-[13px] font-bold text-gray-400">프로젝트 팀이 생성되면 여기에 사무실이 열립니다</span>
            <span className="text-[11px] text-gray-300">python lian_company/main.py 실행 → 팀 자동 배치</span>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {projectTeams.map(p => (
              <ProjectRoom key={p.id} project={p} onMemberClick={onMember} />
            ))}
          </div>
        )}

      </main>

      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} onMemberClick={onMember} />
      {selected && <Modal member={selected.member} teamName={selected.teamName} onClose={() => setSelected(null)} />}
    </div>
  );
}
