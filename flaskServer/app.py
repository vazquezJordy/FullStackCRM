from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import backref, base, relationship
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'app.sqlite2')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Debtor(db.Model, Base):
    __tablename__ = 'debtor'
    id = db.Column(db.Integer, primary_key=True)
    paymentRelationship = db.relationship('Payment', backref="parent_debtor", lazy='joined')
    firstName = db.Column(db.String(25), unique=False)
    lastName = db.Column(db.String(25), unique=False)
    address1 = db.Column(db.String(25), unique=False)
    address2 = db.Column(db.String(25), unique=False)
    phoneNumber = db.Column(db.Integer, unique=False)
    employer = db.Column(db.String(20), unique=False)
    employerPhoneNumber = db.Column(db.Integer, unique=False)
    ssn = db.Column(db.Integer, unique=False)
    spouse = db.Column(db.String(25), unique=False)
    spousePhoneNumber = db.Column(db.Integer, unique=False)
    spouseEmployer = db.Column(db.String(25), unique=False)
    spouseEmployerPhoneNumber = db.Column(db.Integer, unique=False)
    amountOwed = db.Column(db.Integer, unique=False)
    interest = db.Column(db.Integer, unique=False)

    def __init__(self, firstName, lastName, address1, address2, phoneNumber, employer, employerPhoneNumber, ssn, spouse, spousePhoneNumber, spouseEmployer, spouseEmployerPhoneNumber, amountOwed, interest):
        self.firstName = firstName
        self.lastName = lastName
        self.address1 = address1
        self.address2 = address2
        self.phoneNumber = phoneNumber
        self.employer = employer
        self.employerPhoneNumber = employerPhoneNumber
        self.ssn = ssn
        self.spouse = spouse
        self.spousePhoneNumber = spousePhoneNumber
        self.spouseEmployer = spouseEmployer
        self.spouseEmployerPhoneNumber = spouseEmployerPhoneNumber
        self.amountOwed = amountOwed
        self.interest = interest
        
        

class DebtorSchema(ma.Schema):
    class Meta:
        fields = ('firstName', 'lastName', 'address1', 'address2', 'phoneNumber', 'employer', 'employerPhoneNumber', 'ssn', 'spouse',
                  'spousePhoneNumber', 'spouseEmployer', 'spouseEmployerPhoneNumber', 'amountOwed', 'interest', 'id')


debtor_schema = DebtorSchema()
debtors_schema = DebtorSchema(many=True)

@app.route('/addDebtor', methods=['POST'])
def add_debtor():
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    address1 = request.json['address1']
    address2 = request.json['address2']
    phoneNumber = request.json['phoneNumber']
    employer = request.json['employer']
    employerPhoneNumber = request.json['employerPhoneNumber']
    ssn = request.json['ssn']
    spouse = request.json['spouse']
    spousePhoneNumber = request.json['spousePhoneNumber']
    spouseEmployer = request.json['spouseEmployer']
    spouseEmployerPhoneNumber = request.json['spouseEmployerPhoneNumber']
    amountOwed = request.json['amountOwed']
    interest = request.json['interest']

    new_debtor = Debtor(firstName, lastName, address1, address2, phoneNumber, employer, employerPhoneNumber, ssn, spouse, spousePhoneNumber, spouseEmployer, spouseEmployerPhoneNumber, amountOwed, interest)

    db.session.add(new_debtor)
    db.session.commit()

    debtor = Debtor.query.get(new_debtor.id)

    return debtor_schema.jsonify(debtor)

# End point to create a new debtor
@app.route("/debtors", methods=["GET"])
def getAllDebtors():
    all_debtors = Debtor.query.all()
    result = debtors_schema.dump(all_debtors)
    return jsonify(result)

# End point for querying a single user


@app.route("/debtor/<id>", methods=["GET"])
def get_debtor(id):
    debtor = Debtor.query.get(id)
    return debtor_schema.jsonify(debtor)

#Payments
class Payment(db.Model, Base):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, ForeignKey('debtor.id'))
    paymentAmount= db.Column(db.Integer, unique=False)
    dateDue = db.Column(db.String(10), unique=False)
    # parent_debtor = db.relationship("Debtor", backref='paymentRelationship', lazy='joined')
    # debtor_id = db.Column(db.Integer, db.f)

    def __init__(self, parent_id, paymentAmount, dateDue):

        self.parent_id = parent_id
        self.paymentAmount = paymentAmount
        self.dateDue = dateDue
    


class PaymentSchema(ma.Schema):
    class Meta:
        fields = ('parent_id', 'paymentAmount', 'dateDue', 'id')


payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)

@app.route("/debtors", methods=["GET"])

@app.route("/debtor/<id>/payments", methods=["POST"])
def addPayment(id):
    paymentAmount = request.json['paymentAmount']
    dateDue = request.json['dateDue']

    parent_id = id

    newPayment = Payment(parent_id, paymentAmount, dateDue)

    db.session.add(newPayment)
    db.session.commit()

    payment = Payment.query.get(newPayment.id)
    return payment_schema.jsonify(payment)

@app.route("/debtor/<id>/allpayments", methods=["GET"])
def getAllPayments(id):

    payments = Payment.query.filter_by(parent_id = id ).all()
    result = payments_schema.dump(payments)
    return jsonify(result)

#Notes 
class Note(db.Model, Base):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, ForeignKey('debtor.id'))
    note = db.Column(db.String(50), unique=False)

    def __init__(self, parent_id, note):
        self.parent_id = parent_id
        self.note = note

class NoteSchema(ma.Schema):
    class Meta:
        fields = ('id', 'parent_id', 'note')

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


@app.route("/debtor/<id>/note", methods=["POST"])
def addNote(id):
    note = request.json['note']

    parent_id = id

    newNote= Note(parent_id, note)

    db.session.add(newNote)
    db.session.commit()

    note = Note.query.get(newNote.id)
    return note_schema.jsonify(note)

#Phone 

class Phone(db.Model, Base):
    __tablename__ = 'phone'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, ForeignKey('debtor.id'))
    phoneNote = db.Column(db.String(50), unique=False)

    def __init__(self, parent_id, phoneNote):
        self.parent_id = parent_id
        self.phoneNote = phoneNote
        

class PhoneSchema(ma.Schema):
    class Meta:
        fields = ('parent_id', 'id', 'phoneNote')


phoneSchema = PhoneSchema()
phonesSchema = PhoneSchema(many=True)

@app.route("/debtor/<id>/phone", methods=["POST"])
def addPhoneNote(id):
    phoneNote = request.json['phoneNote']
    parent_id = id

    newPhoneNote = Phone(parent_id, phoneNote)
    db.session.add(newPhoneNote)
    db.session.commit()

    phoneNote = Phone.query.get(newPhoneNote.id)

    return phoneSchema.jsonify(phoneNote)

if __name__ == "__main__":
    app.run(debug=True)
