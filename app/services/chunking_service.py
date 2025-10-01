from collections import defaultdict
from typing import List, Optional, Dict, Tuple
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.settings import settings
from app.utils.text_headings import find_headings


class ChunkingService:

    def __init__(self) -> None:

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=settings.chunk_separators,
            add_start_index=True,
            is_separator_regex=False,
        )

    def split_documents(self, docs: List[Document]) -> List[Document]:
        # Split docs by title
        chunks = self._split_docs_by_titles(docs)

        # Split docs recursive
        chunks = self.splitter.split_documents(chunks)

        # Return empty 
        if not chunks:
            return []

        bucket: dict[str, List[int]] = defaultdict(list)
        for i, c in enumerate(chunks):
            key = c.metadata.get("source") or id(c)
            bucket[key].append(i)

        for key, idxs in bucket.items():
            total = len(idxs)
            for local_idx, global_idx in enumerate(idxs, start=1):
                c = chunks[global_idx]
                c.metadata["chunk_index"] = local_idx
                c.metadata["num_chunks"] = total
                if "start_index" in c.metadata:
                    c.metadata["end_index"] = (
                        c.metadata["start_index"] + len(c.page_content)
                    )
                page = c.metadata.get("page") or c.metadata.get("page_number")
                src = c.metadata.get("source", "unknown")
                if page:
                    c.metadata["chunk_id"] = f"{src}#p{page}#c{local_idx}"
                else:
                    c.metadata["chunk_id"] = f"{src}#c{local_idx}"

        return chunks


    def split_text(
        self,
        text: str,
        base_metadata: Optional[Dict[str, str]] = None,
    ) -> List[Document]:
        doc = Document(page_content=text, metadata=base_metadata or {"source": "input_text"})
        return self.split_documents([doc])


    def _split_docs_by_titles(self, docs: List[Document]) -> List[Document]:
        """
        For each Document, detect headings and create section-level Documents.
        If no heading is found, the whole Document becomes a single section.
        """
        out: List[Document] = []
        for d in docs:
            text = d.page_content or ""
            base_meta = dict(d.metadata or {})
            heads = find_headings(text)

            if not heads:
                # No headings: single section
                out.append(self._make_section_doc(
                    text=text,
                    base_meta=base_meta,
                    section_title=base_meta.get("title") or "Document",
                    section_index=1,
                    char_start=0,
                    char_end=len(text),
                ))
                continue

            # Build section ranges from consecutive headings
            ranges: List[Tuple[int, int, str]] = []
            for i, (s, e, title) in enumerate(heads):
                start = s
                end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
                ranges.append((start, end, title))

            # Create section docs
            for idx, (s, e, title) in enumerate(ranges, start=1):
                sec_text = text[s:e].strip()
                if not sec_text:
                    continue
                out.append(self._make_section_doc(
                    text=sec_text,
                    base_meta=base_meta,
                    section_title=title,
                    section_index=idx,
                    char_start=s,
                    char_end=e,
                ))
        return out


    @staticmethod
    def _make_section_doc(
        text: str,
        base_meta: Dict,
        section_title: str,
        section_index: int,
        char_start: int,
        char_end: int,
    ) -> Document:
        meta = {
            **base_meta,
            "section_title": section_title,
            "section_index": section_index,
            "section_char_start": char_start,
            "section_char_end": char_end,
        }
        return Document(page_content=text, metadata=meta)
    
chunk_service = ChunkingService()


if __name__ == "__main__":
    sample_text = (
        "CHÍNH PHỦ\n"
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM – Độc lập - Tự do - Hạnh phúc\n"
        "Số: 181/2025/NĐ-CP            Hà Nội, ngày 01 tháng 7 năm 2025\n"
        "\n"
        "NGHỊ ĐỊNH\n"
        "Quy định chi tiết thi hành một số điều của Luật Thuế giá trị gia tăng\n"
        "\n"
        "Căn cứ Luật Tổ chức Chính phủ ngày 18 tháng 02 năm 2025;\n"
        "Căn cứ Luật Thuế giá trị gia tăng ngày 26 tháng 11 năm 2024;\n"
        "Căn cứ Luật sửa đổi, bổ sung một số điều của Luật Đấu thầu, Luật Đầu tư "
        "theo phương thức đối tác công tư, Luật Hải quan, Luật Thuế giá trị gia tăng, "
        "Luật Thuế xuất khẩu, thuế nhập khẩu, Luật Đầu tư, Luật Đầu tư công, "
        "Luật Quản lý, sử dụng tài sản công ngày 25 tháng 6 năm 2025;\n"
        "Theo đề nghị của Bộ trưởng Bộ Tài chính;\n"
        "Chính phủ ban hành Nghị định quy định chi tiết thi hành một số điều "
        "của Luật Thuế giá trị gia tăng.\n"
        "\n"
        "Chương I\n"
        "NHỮNG QUY ĐỊNH CHUNG\n"
        "\n"
        "Điều 1. Phạm vi điều chỉnh\n"
        "Nghị định này quy định chi tiết về người nộp thuế tại khoản 1, 4 và khoản 5 Điều 4 "
        "và người nộp thuế trong trường hợp nhà cung cấp nước ngoài cung cấp dịch vụ cho người mua "
        "là tổ chức kinh doanh tại Việt Nam áp dụng phương pháp khấu trừ thuế …\n"
        "\n"
        "Điều 2. Đối tượng áp dụng\n"
        "Đối tượng áp dụng của Nghị định này bao gồm:\n"
        "1. Người nộp thuế quy định tại Điều 3 Nghị định này.\n"
        "2. Cơ quan quản lý thuế theo quy định của pháp luật về quản lý thuế.\n"
        "3. Các tổ chức, cá nhân khác có liên quan.\n"
        "\n"
        "Điều 3. Người nộp thuế\n"
        "Người nộp thuế thực hiện theo quy định tại Điều 4 Luật Thuế giá trị gia tăng. "
        "Một số trường hợp được quy định chi tiết như sau:\n"
        "a) Các tổ chức được thành lập và đăng ký kinh doanh theo Luật Doanh nghiệp, "
        "Luật Hợp tác xã và pháp luật chuyên ngành khác.\n"
        "b) Các tổ chức kinh tế của tổ chức chính trị, tổ chức chính trị - xã hội, "
        "tổ chức xã hội, tổ chức xã hội - nghề nghiệp, đơn vị vũ trang nhân dân, "
        "tổ chức sự nghiệp và các tổ chức khác.\n"
        "c) Các doanh nghiệp có vốn đầu tư nước ngoài và bên nước ngoài tham gia "
        "hợp tác kinh doanh theo Luật Đầu tư; các tổ chức, cá nhân nước ngoài hoạt "
        "động kinh doanh ở Việt Nam nhưng không thành lập pháp nhân tại Việt Nam.\n"
    )
    
    chunks = chunk_service.split_text(sample_text, base_metadata={"source": "input_text"})

    print(f"Total chunks: {len(chunks)}")
    for chunk in chunks:
        print("---")
        print(chunk)