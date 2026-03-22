import pickle
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

CATEGORIES = [
    "Loans",
    "Credit Reporting",
    "Bank Services",
    "Debt Collection",
    "Credit Card Services",
]

SAMPLES = {
    "Loans": [
        "My loan application was denied without explanation.",
        "The interest rate on my personal loan was changed without notice.",
        "I was charged hidden fees on my home mortgage.",
        "My student loan servicer applied payments incorrectly.",
        "The auto loan terms were different from what I agreed to.",
        "My mortgage refinancing was delayed for months.",
        "I received a predatory loan offer with extremely high rates.",
        "The lender did not disclose all the loan fees upfront.",
        "My loan modification request was denied repeatedly.",
        "I was approved for a loan but the disbursement never came.",
        "Payday loan company keeps rolling over my debt with high fees.",
        "The bank changed the interest rate on my variable loan without notice.",
        "Home equity loan application has been pending for 6 months.",
        "I was discriminated against in the loan approval process.",
        "My loan payoff amount does not match what was quoted.",
    ],
    "Credit Reporting": [
        "There is an incorrect late payment on my credit report.",
        "A fraudulent account appears on my credit history.",
        "My credit score dropped because of an error I did not cause.",
        "The credit bureau is not correcting the mistake after my dispute.",
        "An account that was paid off still shows as delinquent.",
        "Someone stole my identity and opened accounts in my name.",
        "The credit inquiry I did not authorize is affecting my score.",
        "My credit report shows a debt that has been discharged in bankruptcy.",
        "The same debt is listed multiple times on my credit report.",
        "Credit bureau is not removing outdated information after 7 years.",
        "Inaccurate personal information like wrong address on my report.",
        "My credit freeze was not properly applied by the bureau.",
        "The creditor is reporting a higher balance than what I owe.",
        "I cannot dispute the error because the bureau website is broken.",
        "Hard inquiries on my report from companies I never contacted.",
    ],
    "Bank Services": [
        "My checking account was closed without any warning or reason.",
        "I was charged overdraft fees even though I have overdraft protection.",
        "The bank is holding my direct deposit longer than allowed.",
        "Unauthorized transactions appeared in my savings account.",
        "I cannot access my online banking account and customer service is unhelpful.",
        "The bank charged me a maintenance fee I never agreed to.",
        "My wire transfer was lost and the bank cannot locate it.",
        "The ATM swallowed my card and the bank has not returned it.",
        "I was not notified about a change in my account terms and conditions.",
        "The bank keeps sending my statements to the wrong address.",
        "My joint account was modified without my co-owner's consent.",
        "Bank refused to process my international wire transfer.",
        "Funds were deducted twice for the same transaction.",
        "My account was flagged as suspicious and frozen without notice.",
        "The bank charged foreign transaction fees on domestic purchases.",
    ],
    "Debt Collection": [
        "A debt collector is calling me multiple times a day.",
        "I received a collection notice for a debt that is not mine.",
        "The collector is threatening legal action on a time-barred debt.",
        "A collection agency contacted my employer about my personal debt.",
        "I asked the collector to stop calling but they still contact me.",
        "The debt collector refused to verify the debt I supposedly owe.",
        "I am being harassed by robocalls about a debt.",
        "The collection agency is using abusive language on the phone.",
        "A collector contacted me before 8 AM about an old debt.",
        "The debt I was contacted about was already paid in full.",
        "Collection agency is reporting the wrong amount on my credit file.",
        "I never received a validation notice for this collection account.",
        "A third-party collector keeps contacting family members about my debt.",
        "The collector filed a lawsuit without providing proper notice.",
        "I am receiving collection calls for someone who no longer lives at my address.",
    ],
    "Credit Card Services": [
        "My credit card limit was reduced without any prior notice.",
        "I was charged a foreign transaction fee on an online purchase.",
        "The credit card company is not honoring my dispute for a fraudulent charge.",
        "My rewards points were removed without explanation.",
        "The annual fee was charged even though I cancelled my card.",
        "I am being billed for a subscription I already cancelled.",
        "My credit card was declined despite sufficient available credit.",
        "The card issuer raised my APR without proper notification.",
        "A promotional interest rate was not applied as promised.",
        "My cash back rewards were not credited to my account.",
        "The credit card company failed to process my payment on time.",
        "I was denied a chargeback for a service I never received.",
        "My credit card application was denied due to an error in my profile.",
        "The minimum payment due was changed without informing me.",
        "I am being charged late fees even though I paid on time.",
    ],
}

texts, labels = [], []
for category, sentences in SAMPLES.items():
    for sentence in sentences:
        texts.append(sentence)
        labels.append(category)

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=10000, sublinear_tf=True)),
    ("clf", LogisticRegression(max_iter=1000, C=5.0, solver="lbfgs")),
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
print("=== Model Evaluation ===")
print(classification_report(y_test, y_pred))

import os
model_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(model_dir, "model.pkl")

with open(model_path, "wb") as f:
    pickle.dump({"pipeline": pipeline, "categories": CATEGORIES}, f)

print(f"Model saved → {model_path}")