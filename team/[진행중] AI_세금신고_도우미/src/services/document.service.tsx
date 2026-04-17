// ──────────────────────────────────────────────
// 신고서 문서 생성 서비스
// PDF: @react-pdf/renderer (서버사이드)
// Excel: xlsx (SheetJS)
// 주의: 참고용 초안 — 홈택스 자동 제출 기능 없음
// ──────────────────────────────────────────────

// xlsx (SheetJS) 사용 — 의존성: npm install xlsx
// @react-pdf/renderer — 의존성: npm install @react-pdf/renderer

import * as XLSX from "xlsx";
import { prisma } from "@/lib/prisma";

interface TaxReturnData {
  id: string;
  taxYear: number;
  totalIncome: number;
  totalExpense: number;
  standardDeduction: number;
  taxBase: number;
  estimatedTax: number;
  status: string;
  generatedAt: Date;
  user: {
    email: string;
    name: string | null;
    businessProfile: {
      businessTypeLabel: string;
      taxationType: string;
      registrationNumber: string | null;
    } | null;
  };
}

/**
 * 신고서 Excel 파일 생성
 * @returns Buffer (xlsx binary)
 */
export function generateExcel(data: TaxReturnData): Buffer {
  const wb = XLSX.utils.book_new();

  // ── 시트 1: 신고서 요약 ──
  const summaryData = [
    ["AI 세금신고 도우미 — 종합소득세 신고서 참고용 초안"],
    [`생성일: ${new Date().toLocaleDateString("ko-KR")}`],
    ["⚠️ 이 문서는 참고용입니다. 실제 신고는 홈택스(hometax.go.kr)에서 직접 하세요."],
    [],
    ["== 신고 기본 정보 =="],
    ["귀속연도", `${data.taxYear}년`],
    ["성명", data.user.name ?? "-"],
    ["이메일", data.user.email],
    ["업종", data.user.businessProfile?.businessTypeLabel ?? "-"],
    ["과세유형", formatTaxationType(data.user.businessProfile?.taxationType ?? "")],
    ["사업자등록번호", data.user.businessProfile?.registrationNumber ?? "미입력"],
    [],
    ["== 소득 및 경비 =="],
    ["항목", "금액 (원)", "비고"],
    ["연간 총 수입", formatAmount(data.totalIncome), "사용자 입력값"],
    ["인정 경비", formatAmount(data.totalExpense), "AI 분류 + 단순경비율 적용"],
    ["인적공제 등", formatAmount(data.standardDeduction), "소득세법 §50~51의3"],
    ["과세표준", formatAmount(data.taxBase), "= 총수입 - 경비 - 공제"],
    [],
    ["== 세액 계산 =="],
    ["항목", "금액 (원)", "근거"],
    ["종합소득세", formatAmount(Math.floor(data.estimatedTax / 1.1)), "소득세법 §55 (누진세율)"],
    ["지방소득세", formatAmount(Math.floor(data.estimatedTax - data.estimatedTax / 1.1)), "지방세법 §91 (소득세의 10%)"],
    ["합계 예상 납부세액", formatAmount(data.estimatedTax), "종합소득세 + 지방소득세"],
    [],
    ["== 홈택스 신고 안내 =="],
    ["1단계", "홈택스(hometax.go.kr) 접속 → 로그인"],
    ["2단계", "신고/납부 → 세금신고 → 종합소득세"],
    ["3단계", "정기신고 → 사업소득 선택"],
    ["4단계", "이 문서의 수치를 참고하여 직접 입력"],
    ["5단계", "신고서 제출 및 납부"],
    [],
    ["⚠️ 법적 고지"],
    ["이 문서는 AI가 생성한 참고용 초안입니다."],
    ["세무사법에 따라 세무 대리 행위는 공인된 세무사만 가능합니다."],
    ["AI 계산에는 오류가 있을 수 있으며, 최종 신고 책임은 납세자에게 있습니다."],
    ["복잡한 소득 구조가 있는 경우 세무사 상담을 권장합니다."],
  ];

  const ws = XLSX.utils.aoa_to_sheet(summaryData);

  // 열 너비 설정
  ws["!cols"] = [{ wch: 25 }, { wch: 20 }, { wch: 40 }];

  // 제목 스타일 (xlsx 커뮤니티 에디션은 스타일 미지원, 엔터프라이즈만 가능)
  XLSX.utils.book_append_sheet(wb, ws, "신고서 요약");

  // ── 시트 2: 경비 내역 ──
  // 실제 구현에서는 DB에서 경비 목록을 조회하여 추가
  const expenseHeaders = [["날짜", "상호명", "카테고리", "금액(원)", "업무관련", "사용자확인", "메모"]];
  const expenseWs = XLSX.utils.aoa_to_sheet([
    ...expenseHeaders,
    ["(경비 목록은 대시보드 → 경비 목록에서 확인하세요)", "", "", "", "", "", ""],
  ]);
  expenseWs["!cols"] = [
    { wch: 12 }, { wch: 25 }, { wch: 15 }, { wch: 15 }, { wch: 10 }, { wch: 10 }, { wch: 30 },
  ];
  XLSX.utils.book_append_sheet(wb, expenseWs, "경비 내역");

  const buffer = XLSX.write(wb, { type: "buffer", bookType: "xlsx" });
  return Buffer.from(buffer);
}

/**
 * 신고서 PDF 생성
 * @react-pdf/renderer를 사용한 서버사이드 PDF 렌더링
 * @returns Buffer (pdf binary)
 */
export async function generatePdf(data: TaxReturnData): Promise<Buffer> {
  // @react-pdf/renderer는 동적 import 필요 (Server Component 호환)
  const { renderToBuffer, Document, Page, Text, View, StyleSheet, Font } = await import(
    "@react-pdf/renderer"
  );

  // 나눔고딕 폰트 (한글 지원) — 실제 환경에서는 /public/fonts/ 경로에 폰트 파일 배치 필요
  // Font.register({
  //   family: "NanumGothic",
  //   src: "/fonts/NanumGothic.ttf",
  // });

  const styles = StyleSheet.create({
    page: { padding: 40, fontFamily: "Helvetica", fontSize: 10, color: "#333" },
    title: { fontSize: 18, fontWeight: "bold", marginBottom: 4, color: "#1E3A5F" },
    subtitle: { fontSize: 9, color: "#6b7280", marginBottom: 20 },
    warning: {
      backgroundColor: "#fef3c7",
      border: "1 solid #f59e0b",
      borderRadius: 4,
      padding: 8,
      marginBottom: 16,
      fontSize: 9,
    },
    section: { marginBottom: 16 },
    sectionTitle: {
      fontSize: 12,
      fontWeight: "bold",
      color: "#1E3A5F",
      borderBottom: "1 solid #1E3A5F",
      paddingBottom: 4,
      marginBottom: 8,
    },
    row: { flexDirection: "row", justifyContent: "space-between", marginBottom: 4 },
    label: { color: "#4b5563", flex: 1 },
    value: { fontWeight: "bold", textAlign: "right" },
    highlightRow: {
      flexDirection: "row",
      justifyContent: "space-between",
      backgroundColor: "#1E3A5F",
      padding: "6 8",
      borderRadius: 4,
      marginTop: 8,
    },
    highlightLabel: { color: "#ffffff", fontWeight: "bold" },
    highlightValue: { color: "#22C55E", fontWeight: "bold" },
    disclaimer: {
      marginTop: 24,
      padding: 8,
      backgroundColor: "#f3f4f6",
      borderRadius: 4,
      fontSize: 8,
      color: "#6b7280",
    },
    footer: { position: "absolute", bottom: 30, left: 40, right: 40, fontSize: 8, color: "#9ca3af", textAlign: "center" },
  });

  const incomeTax = Math.floor(data.estimatedTax / 1.1);
  const localTax = data.estimatedTax - incomeTax;

  const pdfDoc = (
    <Document title={`${data.taxYear}년 종합소득세 신고서 (참고용)`} author="AI 세금신고 도우미">
      <Page size="A4" style={styles.page}>
        {/* 헤더 */}
        <Text style={styles.title}>종합소득세 신고서 참고용 초안</Text>
        <Text style={styles.subtitle}>
          생성일: {new Date().toLocaleDateString("ko-KR")} | AI 세금신고 도우미 | 귀속연도: {data.taxYear}년
        </Text>

        {/* 경고 배너 */}
        <View style={styles.warning}>
          <Text>
            ⚠️ 이 문서는 참고용 초안입니다. 실제 신고는 홈택스(hometax.go.kr)에서 직접 진행하세요.
            AI 계산에는 오류가 있을 수 있으며, 최종 신고 책임은 납세자에게 있습니다.
          </Text>
        </View>

        {/* 기본 정보 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>신고자 기본 정보</Text>
          <View style={styles.row}>
            <Text style={styles.label}>성명</Text>
            <Text style={styles.value}>{data.user.name ?? "-"}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>업종</Text>
            <Text style={styles.value}>{data.user.businessProfile?.businessTypeLabel ?? "-"}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>과세유형</Text>
            <Text style={styles.value}>
              {formatTaxationType(data.user.businessProfile?.taxationType ?? "")}
            </Text>
          </View>
          {data.user.businessProfile?.registrationNumber && (
            <View style={styles.row}>
              <Text style={styles.label}>사업자등록번호</Text>
              <Text style={styles.value}>{data.user.businessProfile.registrationNumber}</Text>
            </View>
          )}
        </View>

        {/* 소득 및 경비 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>소득 및 경비 내역</Text>
          <View style={styles.row}>
            <Text style={styles.label}>연간 총 수입</Text>
            <Text style={styles.value}>{formatAmount(data.totalIncome)}원</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>인정 경비 (소득세법 §55)</Text>
            <Text style={styles.value}>- {formatAmount(data.totalExpense)}원</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>인적공제 등 (소득세법 §50~51의3)</Text>
            <Text style={styles.value}>- {formatAmount(data.standardDeduction)}원</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>과세표준</Text>
            <Text style={{ ...styles.value, color: "#1E3A5F" }}>{formatAmount(data.taxBase)}원</Text>
          </View>
        </View>

        {/* 세액 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>예상 세액 (소득세법 §55)</Text>
          <View style={styles.row}>
            <Text style={styles.label}>종합소득세</Text>
            <Text style={styles.value}>{formatAmount(incomeTax)}원</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.label}>지방소득세 (소득세의 10%, 지방세법 §91)</Text>
            <Text style={styles.value}>{formatAmount(localTax)}원</Text>
          </View>
          <View style={styles.highlightRow}>
            <Text style={styles.highlightLabel}>합계 예상 납부세액</Text>
            <Text style={styles.highlightValue}>{formatAmount(data.estimatedTax)}원</Text>
          </View>
        </View>

        {/* 홈택스 신고 안내 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>홈택스 직접 신고 안내</Text>
          <Text style={{ fontSize: 9, lineHeight: 1.6 }}>
            1단계: 홈택스(hometax.go.kr) 접속 → 로그인{"\n"}
            2단계: 신고/납부 → 세금신고 → 종합소득세 → 정기신고{"\n"}
            3단계: 사업소득 선택 → 업종코드 입력{"\n"}
            4단계: 이 문서의 수치를 참고하여 직접 입력{"\n"}
            5단계: 신고서 검토 후 제출 및 납부 (신고기간: 매년 5월 1일~31일)
          </Text>
        </View>

        {/* 법적 고지 */}
        <View style={styles.disclaimer}>
          <Text>
            [법적 고지] 이 신고서는 AI가 생성한 참고용 초안으로, 세무 대리 행위가 아닙니다.
            세무사법에 따라 세무 대리는 공인된 세무사만 가능합니다.
            AI 계산에는 오류가 있을 수 있으며, 최종 신고 및 납세 책임은 납세자에게 있습니다.
            복잡한 소득 구조나 세금 감면 사항이 있는 경우 세무사 상담을 권장합니다.
          </Text>
        </View>

        {/* 푸터 */}
        <Text style={styles.footer}>
          AI 세금신고 도우미 | 이 문서는 참고용입니다 | {new Date().getFullYear()}
        </Text>
      </Page>
    </Document>
  );

  const buffer = await renderToBuffer(pdfDoc);
  return Buffer.from(buffer);
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("ko-KR").format(amount);
}

function formatTaxationType(type: string): string {
  const labels: Record<string, string> = {
    GENERAL: "일반과세자",
    SIMPLIFIED: "간이과세자",
    TAX_FREE: "면세사업자",
    INCOME_ONLY: "소득세만 해당 (프리랜서)",
  };
  return labels[type] ?? type;
}

// React element type for @react-pdf/renderer (dynamic import 호환)
declare namespace JSX {
  interface IntrinsicElements {
    [key: string]: unknown;
  }
}
