import Foundation
import PDFKit

let args = CommandLine.arguments
if args.count < 2 {
    fputs("usage: extract_pdf_text <pdf_path> [start_page] [end_page]\n", stderr)
    exit(2)
}

let pdfPath = args[1]
let startPage = args.count >= 3 ? max(Int(args[2]) ?? 1, 1) : 1
let endPage = args.count >= 4 ? max(Int(args[3]) ?? startPage, startPage) : startPage

guard let document = PDFDocument(url: URL(fileURLWithPath: pdfPath)) else {
    fputs("open failed\n", stderr)
    exit(1)
}

print("PAGES=\(document.pageCount)")
for pageNumber in startPage...min(endPage, document.pageCount) {
    guard let page = document.page(at: pageNumber - 1), let text = page.string else {
        continue
    }
    print("--- PAGE \(pageNumber) ---")
    print(text)
}
