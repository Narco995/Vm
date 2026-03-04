import pandas as pd
import json
import os
from bot.services.ai_service import AIService


class DataService:
    def __init__(self):
        self.ai = AIService()

    async def analyze_file(self, filepath: str, style: str = "structured") -> str:
        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(filepath)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif ext == '.json':
                with open(filepath) as f:
                    data = json.load(f)
                return await self._analyze_json(data, style)
            else:
                return "Unsupported file format."

            return await self._analyze_dataframe(df, style)
        except Exception as e:
            return f"❌ Data analysis error: {str(e)}"

    async def _analyze_dataframe(self, df: pd.DataFrame, style: str) -> str:
        summary = f"""Dataset Summary:
- Shape: {df.shape[0]} rows × {df.shape[1]} columns
- Columns: {', '.join(df.columns.tolist())}
- Data Types: {df.dtypes.to_dict()}
- Missing Values: {df.isnull().sum().to_dict()}
- Numeric Stats:
{df.describe().to_string() if len(df.select_dtypes(include='number').columns) > 0 else 'No numeric columns'}
- Sample (first 3 rows):
{df.head(3).to_string()}"""

        return await self.ai.analyze_data_text(summary, style)

    async def _analyze_json(self, data, style: str) -> str:
        preview = json.dumps(data, indent=2)[:2000]
        summary = f"JSON Data Preview:\n{preview}"
        return await self.ai.analyze_data_text(summary, style)
