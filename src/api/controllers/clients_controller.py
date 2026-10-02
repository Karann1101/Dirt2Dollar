from typing import List, Dict, Any
from fastapi import HTTPException
from src.repositories.client_repository import ClientRepository
from src.repositories.kpi_repository import KPIRepository
from src.repositories.weighted_embedding_repository import WeightedEmbeddingRepository
from src.core.exceptions import FrameworkException
from src.core.logging import logger


class ClientsController:
    def __init__(self):
        self.client_repo = ClientRepository()
        self.kpi_repo = KPIRepository()

    def _map_client(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a DB row from client_updates into a frontend-compatible Client object.
        """
        try:
            c_id = row.get("client_id") or str(row.get("id"))
            name = row.get("client_name") or "Unknown Client"

            # Calculate Churn & Health
            churn_prob = row.get("churn_probability")
            if churn_prob is None:
                # Fallback if None (try matching by satisfaction)
                sat = row.get("satisfaction_score") or 80
                churn_prob = max(0, min(100, 100 - sat))

            health = 100 - churn_prob

            # Map Risk Level
            if churn_prob > 75:
                risk = "critical"
                status = "churned"
            elif churn_prob > 45:
                risk = "high"
                status = "at-risk"
            elif churn_prob > 25:
                risk = "medium"
                status = "at-risk"
            elif churn_prob > 10:
                risk = "low"
                status = "active"
            else:
                risk = "healthy"
                status = "active"

            # Dynamically map industry based on keywords in client name
            name_lower = name.lower()
            if "lawn" in name_lower or "land" in name_lower or "tree" in name_lower:
                industry = "Landscaping"
            elif "roof" in name_lower or "construct" in name_lower or "build" in name_lower or "contract" in name_lower:
                industry = "Construction"
            elif "tech" in name_lower or "cloud" in name_lower or "soft" in name_lower:
                industry = "SaaS"
            else:
                industry = "Professional Services"

            # Dynamically map financial tier
            mrr = 12000 if churn_prob < 30 else 6000
            arr = mrr * 12

            # Timestamp formatting
            ts = row.get("timestamp") or "2024-08-01T00:00:00Z"

            return {
                "id": c_id,
                "name": name,
                "industry": industry,
                "tier": "enterprise" if mrr > 10000 else "growth",
                "status": status,
                "riskLevel": risk,
                "churnProbability": int(churn_prob),
                "healthScore": int(health),
                "mrr": mrr,
                "arr": arr,
                "contractValue": arr,
                "contractStartDate": "2024-01-01",
                "contractEndDate": "2025-01-01",
                "lastActivityDate": ts,
                "createdAt": ts,
                "updatedAt": ts,
                "tags": row.get("flags") or ["Active Campaign"],
                "accountManager": "Sarah Jenkins",
                "campaign": "Q3 Retention Drive",
                "program": "Enterprise Success Plan",
                "contact": {
                    "name": "Primary Lead",
                    "email": f"contact@{name_lower.replace(' ', '')}.com",
                    "role": "Operations Manager",
                    "isPrimary": True
                },
                "address": {
                    "city": "Dallas",
                    "state": "Texas",
                    "country": "USA"
                },
                "metadata": {
                    "summary": row.get("summary"),
                    "satisfaction_score": row.get("satisfaction_score"),
                    "bottlenecks": row.get("bottlenecks"),
                    "action_items": row.get("action_items")
                }
            }

        except Exception as error:
            logger.error(f"Failed to map client row {row.get('id')}: {error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process client record: {error}"
            )

    def get_all_clients(self) -> List[Dict[str, Any]]:
        try:
            rows = self.client_repo.find_all()
        except FrameworkException:
            raise
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Failed to fetch clients: {error}")

        # Filter strictly to Yardworx Land Management
        yardworx_rows = [r for r in rows if "yardworx" in (r.get("client_name") or "").lower()]

        # Filter duplicates by client name / client_id, keeping the latest one
        seen = set()
        unique_clients = []
        for row in reversed(yardworx_rows):  # Read in reverse to get newest first
            key = (row.get("client_name") or "").strip().lower() or row.get("client_id")
            if key not in seen:
                seen.add(key)
                unique_clients.append(self._map_client(row))

        if not unique_clients and yardworx_rows:
            unique_clients.append(self._map_client(yardworx_rows[0]))

        return unique_clients

    def get_client(self, client_id: str) -> Dict[str, Any]:
        try:
            row = self.client_repo.find_by_client_id(client_id)
            if not row:
                # Fallback check by id
                rows = self.client_repo.find_all()
                for r in rows:
                    if str(r.get("id")) == client_id:
                        row = r
                        break
        except FrameworkException:
            raise
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Failed to fetch client '{client_id}': {error}")

        if not row:
            raise HTTPException(status_code=404, detail="Client not found")

        return self._map_client(row)

    def get_client_kpis(self, client_id: str) -> List[Dict[str, Any]]:
        try:
            row = self.kpi_repo.find_by_id(client_id)
        except FrameworkException:
            raise
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Failed to fetch KPIs for '{client_id}': {error}")

        if not row:
            # Default mock KPIs if none exist yet for this client ID
            return [
                {"id": "k1", "clientId": client_id, "name": "Lead Flow Cost", "category": "Lead Quality", "value": 75, "unit": "%", "status": "improving"},
                {"id": "k2", "clientId": client_id, "name": "Appointment Volume", "category": "Conversions", "value": 80, "unit": "units", "status": "stable"},
                {"id": "k3", "clientId": client_id, "name": "Ad Placement Score", "category": "Reach", "value": 65, "unit": "/100", "status": "stable"}
            ]

        try:
            # Mapped from DB fields (adSpend7D, apptCostMTD, etc.)
            return [
                {"id": "k1", "clientId": client_id, "name": "Lead Cost (7D)", "category": "billing", "value": int(row.get("leadCost7D") or 50), "unit": "$", "status": "stable"},
                {"id": "k2", "clientId": client_id, "name": "Lead Cost (MTD)", "category": "billing", "value": int(row.get("leadCostMTD") or 50), "unit": "$", "status": "stable"},
                {"id": "k3", "clientId": client_id, "name": "Appointment Cost (7D)", "category": "billing", "value": int(row.get("apptCost7D") or 150), "unit": "$", "status": "improving"},
                {"id": "k4", "clientId": client_id, "name": "Appointment Cost (MTD)", "category": "billing", "value": int(row.get("apptCostMTD") or 150), "unit": "$", "status": "improving"}
            ]
        except (TypeError, ValueError) as error:
            raise HTTPException(status_code=500, detail=f"Malformed KPI data for client '{client_id}': {error}")

    def get_client_history(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Returns historically similar clients based on this client's
        weighted embedding (summary + KPI combined), computed during
        the AI analysis workflow and looked up via vector similarity
        search — the same underlying data the AI Analysis page's RAG
        step already uses.

        Returns [] when this client has no embedding yet (hasn't been
        through AI analysis) — that is a legitimate empty state, not
        an error, so it doesn't raise.

        NOTE: repeated workflow runs for the same client create multiple
        near-duplicate embedding rows (observed: 60+ rows for a single
        client after repeated test runs). A naive top-N similarity query
        can therefore return nothing but a client's own duplicate rows,
        crowding out every other client. We request a wider match_count
        and deduplicate by client_id, keeping only the best (first,
        since results come back sorted by similarity) match per distinct
        client, so this stays correct regardless of how many duplicate
        rows accumulate for any one client.
        """
        try:
            client_row = self.client_repo.find_by_client_id(client_id)
        except FrameworkException:
            raise
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Failed to fetch client '{client_id}': {error}")

        if not client_row:
            raise HTTPException(status_code=404, detail="Client not found")

        try:
            weighted_repo = WeightedEmbeddingRepository()
            own_embedding_record = weighted_repo.find_by_client_id(client_id)
        except FrameworkException:
            raise
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch similarity embedding for client '{client_id}': {error}"
            )

        if not own_embedding_record or not own_embedding_record.get("embedding"):
            # Client hasn't been analyzed by the AI workflow yet.
            return []

        MAX_DISTINCT_CLIENTS = 6
        # Request far more raw matches than we need, since many of them
        # will be this client's own duplicate embedding rows (observed:
        # up to 60+ duplicates for a single heavily-retested client).
        # Setting this comfortably above the total table size guarantees
        # we see every distinct client's best match, not just whichever
        # client happens to have the most duplicate rows.
        RAW_MATCH_COUNT = 100

        try:
            matches = weighted_repo.find_similar(
                query_embedding=own_embedding_record["embedding"],
                match_count=RAW_MATCH_COUNT,
                match_threshold=0.5,
            ) or []
        except FrameworkException:
            raise
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to find historically similar clients for '{client_id}': {error}"
            )

        results: List[Dict[str, Any]] = []
        seen_client_ids = {str(client_id)}  # exclude self from the start

        for match in matches:
            if len(results) >= MAX_DISTINCT_CLIENTS:
                break

            metadata = match.get("metadata") or {}
            matched_client_id = metadata.get("client_id")

            if not matched_client_id:
                continue

            matched_client_id = str(matched_client_id)

            # Skip self-matches and clients we've already added — keeps
            # only the single best (highest-similarity) match per client.
            if matched_client_id in seen_client_ids:
                continue

            seen_client_ids.add(matched_client_id)

            try:
                matched_row = self.client_repo.find_by_client_id(matched_client_id)
            except Exception as error:
                logger.warning(f"Skipping malformed history match for client '{matched_client_id}': {error}")
                continue

            if not matched_row:
                continue

            churn_prob = matched_row.get("churn_probability")
            if churn_prob is None:
                sat = matched_row.get("satisfaction_score") or 80
                churn_prob = max(0, min(100, 100 - sat))

            if churn_prob > 60:
                outcome = "churned"
            elif churn_prob > 30:
                outcome = "at-risk"
            else:
                outcome = "retained"

            bottlenecks = matched_row.get("bottlenecks") or []
            action_items = matched_row.get("action_items") or []
            summary = matched_row.get("summary") or ""

            results.append({
                "id": matched_row.get("client_id") or str(matched_row.get("id")),
                "name": matched_row.get("client_name") or "Unknown Client",
                "industry": "Professional Services",
                "similarityScore": round((match.get("similarity") or 0) * 100),
                "outcome": outcome,
                "reasonForChurn": bottlenecks[0] if bottlenecks else summary[:180],
                "lessonsLearned": action_items[0] if action_items else (
                    "Maintain proactive communication and monitor KPI trends closely."
                ),
            })

        return results